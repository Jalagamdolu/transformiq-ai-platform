"""Dependency Analysis Engine.

Performs:
  - Validation against self-dependencies
  - Upstream prerequisite traversal
  - Downstream dependent traversal
  - Cycle detection using DFS path tracking to prevent infinite recursion
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Set, Tuple

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.dependency import Dependency


class DependencyEngine:
    """Graph traversal & cycle detection engine for enterprise dependencies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def validate_dependency_creation(
        source_entity_type: str,
        source_entity_id: uuid.UUID,
        target_entity_type: str,
        target_entity_id: uuid.UUID,
    ) -> None:
        """Validate that a dependency does not create a self-reference."""
        if (
            source_entity_type.lower() == target_entity_type.lower()
            and source_entity_id == target_entity_id
        ):
            raise ValueError(
                f"Self-dependency is not allowed: entity {source_entity_type}:{source_entity_id} "
                "cannot depend on itself."
            )

    async def analyze_dependencies(
        self,
        organisation_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        """Perform full multi-hop upstream & downstream dependency traversal with cycle detection."""
        # 1. Fetch all dependencies in the organisation to build memory graph for fast traversal
        stmt = select(Dependency).where(Dependency.organisation_id == organisation_id)
        res = await self.session.execute(stmt)
        all_deps = res.scalars().all()

        # Build adjacency maps:
        # forward_adj[source] -> list of target nodes (downstream dependencies / targets needed)
        # reverse_adj[target] -> list of source nodes (upstream dependencies / who depends on target)
        forward_adj: Dict[Tuple[str, uuid.UUID], List[Dependency]] = {}
        reverse_adj: Dict[Tuple[str, uuid.UUID], List[Dependency]] = {}

        for d in all_deps:
            src_key = (d.source_entity_type, d.source_entity_id)
            tgt_key = (d.target_entity_type, d.target_entity_id)

            forward_adj.setdefault(src_key, []).append(d)
            reverse_adj.setdefault(tgt_key, []).append(d)

        start_node = (entity_type, entity_id)

        # 2. Traverse Upstream (Prerequisites: targets of source_node)
        upstream_prereqs: List[Dict[str, Any]] = []
        visited_upstream: Set[Tuple[str, uuid.UUID]] = {start_node}
        cycles_detected: List[List[str]] = []

        self._dfs_traverse(
            current_node=start_node,
            adj_map=forward_adj,
            is_upstream=True,
            current_path=[start_node],
            visited_global=visited_upstream,
            results=upstream_prereqs,
            cycles=cycles_detected,
            current_depth=0,
            max_depth=max_depth,
        )

        # 3. Traverse Downstream (Dependents: sources depending on target_node)
        downstream_dependents: List[Dict[str, Any]] = []
        visited_downstream: Set[Tuple[str, uuid.UUID]] = {start_node}

        self._dfs_traverse(
            current_node=start_node,
            adj_map=reverse_adj,
            is_upstream=False,
            current_path=[start_node],
            visited_global=visited_downstream,
            results=downstream_dependents,
            cycles=cycles_detected,
            current_depth=0,
            max_depth=max_depth,
        )

        return {
            "upstream_prerequisites": upstream_prereqs,
            "downstream_dependents": downstream_dependents,
            "has_cycles": len(cycles_detected) > 0,
            "cycle_paths": [
                " -> ".join([f"{t}:{i}" for t, i in path]) for path in cycles_detected
            ],
        }

    def _dfs_traverse(
        self,
        current_node: Tuple[str, uuid.UUID],
        adj_map: Dict[Tuple[str, uuid.UUID], List[Dependency]],
        is_upstream: bool,
        current_path: List[Tuple[str, uuid.UUID]],
        visited_global: Set[Tuple[str, uuid.UUID]],
        results: List[Dict[str, Any]],
        cycles: List[List[Tuple[str, uuid.UUID]]],
        current_depth: int,
        max_depth: int,
    ) -> None:
        if current_depth >= max_depth:
            return

        edges = adj_map.get(current_node, [])
        for edge in edges:
            next_node = (
                (edge.target_entity_type, edge.target_entity_id)
                if is_upstream
                else (edge.source_entity_type, edge.source_entity_id)
            )

            # Cycle detection: if next_node is in current_path stack
            if next_node in current_path:
                cycle_path = current_path + [next_node]
                if cycle_path not in cycles:
                    cycles.append(cycle_path)
                continue

            # Record dependency finding
            if next_node not in visited_global:
                visited_global.add(next_node)
                results.append(
                    {
                        "dependency_id": str(edge.id),
                        "entity_type": next_node[0],
                        "entity_id": str(next_node[1]),
                        "relationship_type": edge.relationship_type,
                        "description": edge.description,
                        "depth": current_depth + 1,
                    }
                )

                self._dfs_traverse(
                    current_node=next_node,
                    adj_map=adj_map,
                    is_upstream=is_upstream,
                    current_path=current_path + [next_node],
                    visited_global=visited_global,
                    results=results,
                    cycles=cycles,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                )
