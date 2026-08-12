"""Enterprise Impact Engine.

Traverses database relationships to discover the full organisational context
and affected entities for a given transformation scenario, process, or AI opportunity.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Activity,
    AIOpportunity,
    Governance,
    Organisation,
    Process,
    Role,
    Skill,
    Strategy,
    TransformationInitiative,
    ValueChain,
)


class ImpactEngine:
    """Traverses PostgreSQL relationships to compute affected enterprise entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def discover_impact(
        self,
        organisation_id: uuid.UUID,
        opportunity_id: Optional[uuid.UUID] = None,
        process_id: Optional[uuid.UUID] = None,
        strategy_id: Optional[uuid.UUID] = None,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
        """Traverse relationships to discover affected entities and governance records.

        Returns:
            (affected_entities_dict, governance_findings_list, context_meta_dict)
        """
        affected_value_chains: List[ValueChain] = []
        affected_processes: List[Process] = []
        affected_activities: List[Activity] = []
        affected_opportunities: List[AIOpportunity] = []
        affected_roles: List[Role] = []
        affected_skills: List[Skill] = []
        affected_initiatives: List[TransformationInitiative] = []
        governance_records: List[Governance] = []

        context_meta: Dict[str, Any] = {
            "primary_opportunity_name": None,
            "primary_opportunity_status": None,
            "primary_ai_technology": None,
        }

        # ── Case 1: Specific AI Opportunity provided ────────────────────────── #
        if opportunity_id:
            stmt = (
                select(AIOpportunity)
                .where(
                    AIOpportunity.id == opportunity_id,
                    AIOpportunity.organisation_id == organisation_id,
                )
                .options(
                    selectinload(AIOpportunity.process).selectinload(Process.value_chain),
                    selectinload(AIOpportunity.roles),
                    selectinload(AIOpportunity.skills),
                    selectinload(AIOpportunity.governance_records),
                    selectinload(AIOpportunity.transformation_initiatives),
                )
            )
            res = await self.session.execute(stmt)
            opp = res.scalar_one_or_none()

            if opp:
                affected_opportunities.append(opp)
                context_meta["primary_opportunity_name"] = opp.name
                context_meta["primary_opportunity_status"] = opp.status
                context_meta["primary_ai_technology"] = opp.ai_technology

                # Governance
                governance_records.extend(opp.governance_records)

                # Initiatives
                affected_initiatives.extend(opp.transformation_initiatives)

                # Roles & Skills directly on Opportunity
                affected_roles.extend(opp.roles)
                affected_skills.extend(opp.skills)

                # Process & ValueChain
                if opp.process:
                    affected_processes.append(opp.process)
                    if opp.process.value_chain:
                        affected_value_chains.append(opp.process.value_chain)

                    # Activities under process
                    act_stmt = (
                        select(Activity)
                        .where(Activity.process_id == opp.process.id)
                        .options(
                            selectinload(Activity.roles),
                            selectinload(Activity.skills),
                        )
                    )
                    act_res = await self.session.execute(act_stmt)
                    acts = act_res.scalars().all()
                    affected_activities.extend(acts)

                    for act in acts:
                        affected_roles.extend(act.roles)
                        affected_skills.extend(act.skills)

        # ── Case 2: Specific Process provided ───────────────────────────────── #
        elif process_id:
            proc_stmt = (
                select(Process)
                .where(
                    Process.id == process_id,
                    Process.organisation_id == organisation_id,
                )
                .options(
                    selectinload(Process.value_chain),
                    selectinload(Process.activities).selectinload(Activity.roles),
                    selectinload(Process.activities).selectinload(Activity.skills),
                    selectinload(Process.ai_opportunities).selectinload(
                        AIOpportunity.governance_records
                    ),
                    selectinload(Process.ai_opportunities).selectinload(
                        AIOpportunity.transformation_initiatives
                    ),
                )
            )
            proc_res = await self.session.execute(proc_stmt)
            proc = proc_res.scalar_one_or_none()

            if proc:
                affected_processes.append(proc)
                if proc.value_chain:
                    affected_value_chains.append(proc.value_chain)

                affected_activities.extend(proc.activities)
                for act in proc.activities:
                    affected_roles.extend(act.roles)
                    affected_skills.extend(act.skills)

                for opp in proc.ai_opportunities:
                    affected_opportunities.append(opp)
                    governance_records.extend(opp.governance_records)
                    affected_initiatives.extend(opp.transformation_initiatives)

        # ── Fallback: Discover top-level organisation context ───────────────── #
        else:
            proc_stmt = (
                select(Process)
                .where(Process.organisation_id == organisation_id)
                .limit(5)
            )
            proc_res = await self.session.execute(proc_stmt)
            affected_processes.extend(proc_res.scalars().all())

            opp_stmt = (
                select(AIOpportunity)
                .where(AIOpportunity.organisation_id == organisation_id)
                .limit(5)
            )
            opp_res = await self.session.execute(opp_stmt)
            affected_opportunities.extend(opp_res.scalars().all())

        # Deduplicate entities by ID
        unique_vcs = self._dedupe_entities(affected_value_chains)
        unique_procs = self._dedupe_entities(affected_processes)
        unique_acts = self._dedupe_entities(affected_activities)
        unique_opps = self._dedupe_entities(affected_opportunities)
        unique_roles = self._dedupe_entities(affected_roles)
        unique_skills = self._dedupe_entities(affected_skills)
        unique_inits = self._dedupe_entities(affected_initiatives)
        unique_govs = self._dedupe_entities(governance_records)

        affected_entities_dict = {
            "value_chains": [
                {"id": str(vc.id), "name": vc.name} for vc in unique_vcs
            ],
            "processes": [
                {"id": str(p.id), "name": p.name, "process_type": p.process_type}
                for p in unique_procs
            ],
            "activities": [
                {"id": str(a.id), "name": a.name, "activity_type": a.activity_type}
                for a in unique_acts
            ],
            "ai_opportunities": [
                {"id": str(o.id), "name": o.name, "category": o.category}
                for o in unique_opps
            ],
            "roles": [
                {"id": str(r.id), "name": r.name, "department": r.department}
                for r in unique_roles
            ],
            "skills": [
                {"id": str(s.id), "name": s.name, "skill_type": s.skill_type}
                for s in unique_skills
            ],
            "transformation_initiatives": [
                {"id": str(i.id), "name": i.name, "status": i.status}
                for i in unique_inits
            ],
        }

        governance_findings_list = [
            {
                "id": str(g.id),
                "ai_opportunity_id": str(g.ai_opportunity_id),
                "category": g.category,
                "risk_level": g.risk_level,
                "description": g.description,
                "notes": g.notes,
            }
            for g in unique_govs
        ]

        return affected_entities_dict, governance_findings_list, context_meta

    @staticmethod
    def _dedupe_entities(entities: List[Any]) -> List[Any]:
        seen: Set[uuid.UUID] = set()
        deduped = []
        for e in entities:
            if e.id not in seen:
                seen.add(e.id)
                deduped.append(e)
        return deduped
