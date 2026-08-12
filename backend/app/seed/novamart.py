"""Synthetic NovaMart seed data population script."""

from __future__ import annotations

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Activity,
    AIOpportunity,
    Dependency,
    Governance,
    Organisation,
    Process,
    Role,
    Skill,
    Strategy,
    TransformationInitiative,
    ValueChain,
)

logger = logging.getLogger("app.seed")


async def seed_novamart_data(session: AsyncSession) -> Organisation:
    """Seed the database with synthetic NovaMart enterprise data.

    Returns the seeded Organisation instance.
    """
    # Check if NovaMart already exists
    stmt = select(Organisation).where(Organisation.name == "NovaMart")
    res = await session.execute(stmt)
    existing = res.scalar_one_or_none()
    if existing:
        logger.info("NovaMart organisation already exists. Refreshing seed data...")
        await session.delete(existing)
        await session.flush()

    logger.info("Seeding NovaMart synthetic enterprise dataset...")

    # 1. Organisation
    org = Organisation(
        name="NovaMart",
        industry="Retail",
        description="Major national retail chain operating 500+ supermarket and omnichannel stores.",
        is_active=True,
    )
    session.add(org)
    await session.flush()

    # 2. Strategies
    strat1 = Strategy(
        organisation_id=org.id,
        name="Become an AI-enabled retailer within three years",
        description="Embed artificial intelligence and automation across key retail processes to improve operating margin by 300bps.",
        status="active",
        time_horizon="2025-2028",
    )
    strat2 = Strategy(
        organisation_id=org.id,
        name="Optimize omnichannel supply chain resiliency",
        description="Build end-to-end real-time inventory visibility and automated replenishment to reduce stockouts below 2%.",
        status="active",
        time_horizon="2025-2027",
    )
    strat3 = Strategy(
        organisation_id=org.id,
        name="Enhance customer hyper-personalization & loyalty",
        description="Leverage customer preference data to deliver targeted offers and seamless customer service across web, app, and store.",
        status="active",
        time_horizon="2026-2028",
    )
    session.add_all([strat1, strat2, strat3])
    await session.flush()

    # 3. Value Chains
    vc_supply = ValueChain(
        organisation_id=org.id,
        strategy_id=strat2.id,
        name="Supply Chain & Merchandising",
        description="End-to-end procurement, inventory management, demand forecasting, and logistics.",
    )
    vc_ops = ValueChain(
        organisation_id=org.id,
        strategy_id=strat1.id,
        name="Store & Digital Operations",
        description="Physical store management, e-commerce fulfillment, planogram execution, and store workforce.",
    )
    vc_cx = ValueChain(
        organisation_id=org.id,
        strategy_id=strat3.id,
        name="Customer Experience & Marketing",
        description="Customer loyalty programs, targeted marketing, customer support, and personalized pricing.",
    )
    vc_corporate = ValueChain(
        organisation_id=org.id,
        strategy_id=strat1.id,
        name="Corporate & Shared Services",
        description="Finance, human resources, IT infrastructure, legal, and compliance.",
    )
    session.add_all([vc_supply, vc_ops, vc_cx, vc_corporate])
    await session.flush()

    # 4. Roles
    role_planner = Role(organisation_id=org.id, name="Demand Planner", department="Supply Chain", description="Manages SKU demand forecasts and safety stock levels.")
    role_sc_analyst = Role(organisation_id=org.id, name="Supply Chain Analyst", department="Logistics", description="Monitors supplier lead times and warehouse throughput.")
    role_category_mgr = Role(organisation_id=org.id, name="Category Manager", department="Merchandising", description="Responsible for product assortment and supplier negotiations.")
    role_store_mgr = Role(organisation_id=org.id, name="Store Manager", department="Retail Operations", description="Oversees store staffing, inventory receiving, and customer experience.")
    role_mkt_spec = Role(organisation_id=org.id, name="Marketing Specialist", department="Marketing", description="Executes promotional campaigns and loyalty rewards.")
    role_support_lead = Role(organisation_id=org.id, name="Customer Support Lead", department="Customer Care", description="Handles complex customer service inquiries and refunds.")
    role_pricing_analyst = Role(organisation_id=org.id, name="Pricing Analyst", department="Finance", description="Analyzes price elasticity and competitor pricing.")
    role_inv_controller = Role(organisation_id=org.id, name="Inventory Controller", department="Warehouse Operations", description="Audits inventory accuracy and manages stock counts.")
    session.add_all([
        role_planner, role_sc_analyst, role_category_mgr, role_store_mgr,
        role_mkt_spec, role_support_lead, role_pricing_analyst, role_inv_controller
    ])
    await session.flush()

    # 5. Skills
    skill_forecasting = Skill(organisation_id=org.id, name="Demand Forecasting", skill_type="business", description="Ability to project customer demand patterns.")
    skill_sc_analytics = Skill(organisation_id=org.id, name="Supply Chain Analytics", skill_type="data", description="Quantitative modeling of supply chain metrics.")
    skill_data_analysis = Skill(organisation_id=org.id, name="Data Analysis", skill_type="data", description="Extracting insights from structured operational data.")
    skill_inv_opt = Skill(organisation_id=org.id, name="Inventory Optimization", skill_type="technical", description="Determining optimal reorder points and safety stocks.")
    skill_ai_oversight = Skill(organisation_id=org.id, name="AI Oversight", skill_type="ai_literacy", description="Monitoring AI recommendation outputs for quality and safety.")
    skill_cs_mgmt = Skill(organisation_id=org.id, name="Customer Service Management", skill_type="leadership", description="Managing customer communications and conflict resolution.")
    skill_price_modeling = Skill(organisation_id=org.id, name="Price Modeling", skill_type="technical", description="Modeling promotional elasticity and competitor dynamic pricing.")
    skill_omni_ops = Skill(organisation_id=org.id, name="Omnichannel Operations", skill_type="business", description="Executing click-and-collect and ship-from-store operations.")
    skill_prompt_eng = Skill(organisation_id=org.id, name="Prompt Engineering", skill_type="ai_literacy", description="Crafting effective prompts for LLM assistant toolsets.")
    skill_sql = Skill(organisation_id=org.id, name="SQL & Data Querying", skill_type="technical", description="Querying enterprise data warehouses.")
    session.add_all([
        skill_forecasting, skill_sc_analytics, skill_data_analysis, skill_inv_opt,
        skill_ai_oversight, skill_cs_mgmt, skill_price_modeling, skill_omni_ops,
        skill_prompt_eng, skill_sql
    ])
    await session.flush()

    # 6. Processes & Activities
    # Process 1: Demand Forecasting
    proc_df = Process(
        organisation_id=org.id,
        value_chain_id=vc_supply.id,
        name="Demand Forecasting",
        description="Predicting store and warehouse SKU-level demand using historical sales and external factors.",
        process_type="operational",
        status="active",
    )
    # Process 2: Supplier Order Fulfillment
    proc_sof = Process(
        organisation_id=org.id,
        value_chain_id=vc_supply.id,
        name="Supplier Order Fulfillment",
        description="Placing purchase orders with suppliers and tracking inbound shipments to distribution centers.",
        process_type="operational",
        status="active",
    )
    # Process 3: Store Inventory Management
    proc_sim = Process(
        organisation_id=org.id,
        value_chain_id=vc_ops.id,
        name="Store Inventory Management",
        description="Receiving, stocking, cycle counting, and shelf management in retail stores.",
        process_type="operational",
        status="active",
    )
    # Process 4: Assortment Planning
    proc_ap = Process(
        organisation_id=org.id,
        value_chain_id=vc_supply.id,
        name="Assortment Planning",
        description="Selecting product mix per region and store tier to optimize margin and shelf space.",
        process_type="strategic",
        status="active",
    )
    # Process 5: Price & Markdown Optimization
    proc_po = Process(
        organisation_id=org.id,
        value_chain_id=vc_cx.id,
        name="Price Optimization",
        description="Determining base pricing, promotional discounts, and end-of-season markdown timing.",
        process_type="operational",
        status="active",
    )
    # Process 6: Checkout & Payment Processing
    proc_pay = Process(
        organisation_id=org.id,
        value_chain_id=vc_ops.id,
        name="Checkout & Payment Processing",
        description="POS transaction handling, self-checkout oversight, and digital wallet integration.",
        process_type="operational",
        status="active",
    )
    # Process 7: Customer Support & Inquiries
    proc_cs = Process(
        organisation_id=org.id,
        value_chain_id=vc_cx.id,
        name="Customer Support & Inquiries",
        description="Handling omnichannel customer inquiries, order tracking issues, and returns.",
        process_type="support",
        status="active",
    )
    # Process 8: Personalized Marketing & Promotions
    proc_pm = Process(
        organisation_id=org.id,
        value_chain_id=vc_cx.id,
        name="Personalized Promotions",
        description="Creating and dispatching targeted digital coupons and loyalty incentives.",
        process_type="operational",
        status="active",
    )
    # Process 9: Workforce Scheduling
    proc_ws = Process(
        organisation_id=org.id,
        value_chain_id=vc_ops.id,
        name="Workforce Scheduling",
        description="Staff shift planning and labor budget optimization based on store foot-traffic trends.",
        process_type="management",
        status="active",
    )
    # Process 10: Financial Reconciliation
    proc_fr = Process(
        organisation_id=org.id,
        value_chain_id=vc_corporate.id,
        name="Financial Reconciliation",
        description="Daily sales auditing, vendor invoice matching, and bank deposit reconciliation.",
        process_type="support",
        status="active",
    )

    session.add_all([
        proc_df, proc_sof, proc_sim, proc_ap, proc_po,
        proc_pay, proc_cs, proc_pm, proc_ws, proc_fr
    ])
    await session.flush()

    # Activities (20+)
    acts = [
        # Demand Forecasting
        Activity(process_id=proc_df.id, name="Analyse historical sales data", description="Extract 24-month store sales history", activity_type="manual", sequence_order=1),
        Activity(process_id=proc_df.id, name="Generate baseline demand forecast", description="Calculate statistical baseline forecast", activity_type="automated", sequence_order=2),
        Activity(process_id=proc_df.id, name="Review forecast anomalies", description="Demand planner validates weather/promo spikes", activity_type="review", sequence_order=3),
        Activity(process_id=proc_df.id, name="Approve final SKU order quantities", description="Sign off on weekly replenishment plan", activity_type="decision", sequence_order=4),
        # Supplier Order Fulfillment
        Activity(process_id=proc_sof.id, name="Generate automated purchase orders", description="Create POs based on reorder thresholds", activity_type="automated", sequence_order=1),
        Activity(process_id=proc_sof.id, name="Track supplier shipment ASN", description="Monitor advance shipping notices", activity_type="automated", sequence_order=2),
        Activity(process_id=proc_sof.id, name="Inspect warehouse receiving goods", description="Quality and quantity check at dock", activity_type="manual", sequence_order=3),
        # Store Inventory Management
        Activity(process_id=proc_sim.id, name="Receive store stock delivery", description="Scan delivery pallets into inventory system", activity_type="manual", sequence_order=1),
        Activity(process_id=proc_sim.id, name="Perform high-shrink cycle count", description="Weekly audit of high-value SKUs", activity_type="manual", sequence_order=2),
        Activity(process_id=proc_sim.id, name="Audit shelf planogram compliance", description="Verify physical shelf layouts match layout plan", activity_type="review", sequence_order=3),
        # Assortment Planning
        Activity(process_id=proc_ap.id, name="Evaluate category SKU performance", description="Review sell-through rates and profit margins", activity_type="manual", sequence_order=1),
        Activity(process_id=proc_ap.id, name="Select regional SKU mix", description="Finalize product selection per store cluster", activity_type="decision", sequence_order=2),
        # Price Optimization
        Activity(process_id=proc_po.id, name="Scrape market competitor prices", description="Collect benchmark prices from competing retailers", activity_type="automated", sequence_order=1),
        Activity(process_id=proc_po.id, name="Calculate promotional elasticities", description="Model volume lift against discount percent", activity_type="automated", sequence_order=2),
        Activity(process_id=proc_po.id, name="Approve promotional price changes", description="Category manager review and signoff", activity_type="decision", sequence_order=3),
        # Checkout & Payment
        Activity(process_id=proc_pay.id, name="Process customer POS basket", description="Scan items and calculate totals", activity_type="automated", sequence_order=1),
        Activity(process_id=proc_pay.id, name="Verify fraud risk score", description="Real-time payment risk check for digital orders", activity_type="automated", sequence_order=2),
        # Customer Support
        Activity(process_id=proc_cs.id, name="Ingest customer inquiry ticket", description="Route inquiry from chat, email, or call center", activity_type="automated", sequence_order=1),
        Activity(process_id=proc_cs.id, name="Search policy & order history", description="Find customer order status and return policies", activity_type="manual", sequence_order=2),
        Activity(process_id=proc_cs.id, name="Issue refund or replacement", description="Process resolution in CRM", activity_type="decision", sequence_order=3),
        # Personalized Promotions
        Activity(process_id=proc_pm.id, name="Segment loyalty customer profiles", description="Cluster customers by purchase affinity", activity_type="automated", sequence_order=1),
        Activity(process_id=proc_pm.id, name="Generate personalized coupon offers", description="Match active promotions to customer segments", activity_type="automated", sequence_order=2),
        # Workforce Scheduling
        Activity(process_id=proc_ws.id, name="Forecast store foot traffic", description="Project labor hours needed per store hour", activity_type="automated", sequence_order=1),
        Activity(process_id=proc_ws.id, name="Publish store shift roster", description="Assign store associates to shifts", activity_type="decision", sequence_order=2),
    ]
    session.add_all(acts)
    await session.flush()

    # 7. AI Opportunities (8+)
    opp1 = AIOpportunity(
        organisation_id=org.id,
        process_id=proc_df.id,
        name="AI-Powered Demand Forecasting",
        description="Machine learning model predicting SKU demand using weather, holidays, and localized store trends.",
        category="automation",
        status="approved",
        ai_technology="Time-Series Transformers / XGBoost",
    )
    opp2 = AIOpportunity(
        organisation_id=org.id,
        process_id=proc_po.id,
        name="Dynamic Markdown & Price Optimization",
        description="Reinforcement learning agent optimizing end-of-season clearance markdowns to maximize net margin.",
        category="optimization",
        status="assessed",
        ai_technology="Reinforcement Learning / Price Elasticity Net",
    )
    opp3 = AIOpportunity(
        organisation_id=org.id,
        process_id=proc_sof.id,
        name="Automated Supplier Replenishment Assistant",
        description="Autonomous agent monitoring warehouse safety stocks and issuing PO recommendations.",
        category="automation",
        status="in_progress",
        ai_technology="LLM Agent / Rule-Engine Hybrid",
    )
    opp4 = AIOpportunity(
        organisation_id=org.id,
        process_id=proc_ap.id,
        name="Smart Assortment Recommendation Engine",
        description="Clustering algorithm recommending store-level product assortments based on local demographics.",
        category="analytics",
        status="identified",
        ai_technology="Collaborative Filtering & Spatial Clustering",
    )
    opp5 = AIOpportunity(
        organisation_id=org.id,
        process_id=proc_cs.id,
        name="Customer Support Copilot",
        description="LLM assistant retrieving order history and store policies to draft response suggestions for agents.",
        category="augmentation",
        status="in_progress",
        ai_technology="RAG / Enterprise LLM",
    )
    opp6 = AIOpportunity(
        organisation_id=org.id,
        process_id=proc_sim.id,
        name="Visual Planogram Compliance Inspector",
        description="Computer vision model analyzing shelf camera photos to flag out-of-stock items and misplaced SKUs.",
        category="automation",
        status="identified",
        ai_technology="Computer Vision / YOLOv8",
    )
    opp7 = AIOpportunity(
        organisation_id=org.id,
        process_id=proc_pay.id,
        name="Predictive Shrink & Fraud Detection",
        description="Anomaly detection model scanning POS transaction streams for high-risk self-checkout fraud patterns.",
        category="analytics",
        status="identified",
        ai_technology="Isolation Forest / Anomaly Detection",
    )
    opp8 = AIOpportunity(
        organisation_id=org.id,
        process_id=proc_pm.id,
        name="Real-Time Personalization Engine",
        description="Generative AI creating tailored promotional email/SMS copy based on loyalty purchase history.",
        category="generation",
        status="identified",
        ai_technology="Generative LLM / Personalization Engine",
    )

    session.add_all([opp1, opp2, opp3, opp4, opp5, opp6, opp7, opp8])
    await session.flush()

    # Link Activity ↔ Role, Activity ↔ Skill, Opportunity ↔ Role, Opportunity ↔ Skill
    from app.db.models.associations import (
        activity_roles,
        activity_skills,
        opportunity_roles,
        opportunity_skills,
    )
    from sqlalchemy import insert

    # Activity ↔ Role
    await session.execute(
        insert(activity_roles).values([
            {"activity_id": acts[0].id, "role_id": role_planner.id},
            {"activity_id": acts[0].id, "role_id": role_sc_analyst.id},
            {"activity_id": acts[1].id, "role_id": role_planner.id},
            {"activity_id": acts[1].id, "role_id": role_sc_analyst.id},
            {"activity_id": acts[2].id, "role_id": role_planner.id},
            {"activity_id": acts[3].id, "role_id": role_planner.id},
            {"activity_id": acts[3].id, "role_id": role_sc_analyst.id},
            {"activity_id": acts[4].id, "role_id": role_planner.id},
            {"activity_id": acts[4].id, "role_id": role_sc_analyst.id},
            {"activity_id": acts[5].id, "role_id": role_sc_analyst.id},
            {"activity_id": acts[6].id, "role_id": role_inv_controller.id},
            {"activity_id": acts[7].id, "role_id": role_inv_controller.id},
            {"activity_id": acts[7].id, "role_id": role_store_mgr.id},
            {"activity_id": acts[8].id, "role_id": role_inv_controller.id},
            {"activity_id": acts[9].id, "role_id": role_store_mgr.id},
            {"activity_id": acts[10].id, "role_id": role_category_mgr.id},
            {"activity_id": acts[11].id, "role_id": role_category_mgr.id},
            {"activity_id": acts[12].id, "role_id": role_pricing_analyst.id},
            {"activity_id": acts[13].id, "role_id": role_pricing_analyst.id},
            {"activity_id": acts[14].id, "role_id": role_pricing_analyst.id},
            {"activity_id": acts[14].id, "role_id": role_category_mgr.id},
            {"activity_id": acts[17].id, "role_id": role_support_lead.id},
            {"activity_id": acts[18].id, "role_id": role_support_lead.id},
            {"activity_id": acts[19].id, "role_id": role_support_lead.id},
        ])
    )

    # Activity ↔ Skill
    await session.execute(
        insert(activity_skills).values([
            {"activity_id": acts[0].id, "skill_id": skill_data_analysis.id},
            {"activity_id": acts[0].id, "skill_id": skill_forecasting.id},
            {"activity_id": acts[1].id, "skill_id": skill_forecasting.id},
            {"activity_id": acts[1].id, "skill_id": skill_sc_analytics.id},
            {"activity_id": acts[2].id, "skill_id": skill_ai_oversight.id},
            {"activity_id": acts[2].id, "skill_id": skill_data_analysis.id},
            {"activity_id": acts[3].id, "skill_id": skill_forecasting.id},
            {"activity_id": acts[3].id, "skill_id": skill_inv_opt.id},
            {"activity_id": acts[4].id, "skill_id": skill_inv_opt.id},
            {"activity_id": acts[4].id, "skill_id": skill_sc_analytics.id},
            {"activity_id": acts[5].id, "skill_id": skill_sc_analytics.id},
            {"activity_id": acts[6].id, "skill_id": skill_inv_opt.id},
            {"activity_id": acts[7].id, "skill_id": skill_omni_ops.id},
            {"activity_id": acts[8].id, "skill_id": skill_inv_opt.id},
            {"activity_id": acts[9].id, "skill_id": skill_omni_ops.id},
            {"activity_id": acts[9].id, "skill_id": skill_ai_oversight.id},
            {"activity_id": acts[10].id, "skill_id": skill_data_analysis.id},
            {"activity_id": acts[11].id, "skill_id": skill_forecasting.id},
            {"activity_id": acts[12].id, "skill_id": skill_data_analysis.id},
            {"activity_id": acts[12].id, "skill_id": skill_sql.id},
            {"activity_id": acts[13].id, "skill_id": skill_price_modeling.id},
            {"activity_id": acts[14].id, "skill_id": skill_price_modeling.id},
            {"activity_id": acts[17].id, "skill_id": skill_cs_mgmt.id},
            {"activity_id": acts[18].id, "skill_id": skill_prompt_eng.id},
            {"activity_id": acts[18].id, "skill_id": skill_cs_mgmt.id},
            {"activity_id": acts[19].id, "skill_id": skill_cs_mgmt.id},
        ])
    )

    # Opportunity ↔ Role
    await session.execute(
        insert(opportunity_roles).values([
            {"opportunity_id": opp1.id, "role_id": role_planner.id},
            {"opportunity_id": opp1.id, "role_id": role_sc_analyst.id},
            {"opportunity_id": opp2.id, "role_id": role_pricing_analyst.id},
            {"opportunity_id": opp2.id, "role_id": role_category_mgr.id},
            {"opportunity_id": opp3.id, "role_id": role_planner.id},
            {"opportunity_id": opp3.id, "role_id": role_inv_controller.id},
            {"opportunity_id": opp4.id, "role_id": role_category_mgr.id},
            {"opportunity_id": opp5.id, "role_id": role_support_lead.id},
            {"opportunity_id": opp6.id, "role_id": role_store_mgr.id},
            {"opportunity_id": opp7.id, "role_id": role_inv_controller.id},
            {"opportunity_id": opp7.id, "role_id": role_store_mgr.id},
            {"opportunity_id": opp8.id, "role_id": role_mkt_spec.id},
        ])
    )

    # Opportunity ↔ Skill
    await session.execute(
        insert(opportunity_skills).values([
            {"opportunity_id": opp1.id, "skill_id": skill_forecasting.id},
            {"opportunity_id": opp1.id, "skill_id": skill_sc_analytics.id},
            {"opportunity_id": opp1.id, "skill_id": skill_ai_oversight.id},
            {"opportunity_id": opp2.id, "skill_id": skill_price_modeling.id},
            {"opportunity_id": opp2.id, "skill_id": skill_data_analysis.id},
            {"opportunity_id": opp3.id, "skill_id": skill_inv_opt.id},
            {"opportunity_id": opp3.id, "skill_id": skill_ai_oversight.id},
            {"opportunity_id": opp4.id, "skill_id": skill_data_analysis.id},
            {"opportunity_id": opp4.id, "skill_id": skill_sc_analytics.id},
            {"opportunity_id": opp5.id, "skill_id": skill_cs_mgmt.id},
            {"opportunity_id": opp5.id, "skill_id": skill_prompt_eng.id},
            {"opportunity_id": opp5.id, "skill_id": skill_ai_oversight.id},
            {"opportunity_id": opp6.id, "skill_id": skill_omni_ops.id},
            {"opportunity_id": opp6.id, "skill_id": skill_ai_oversight.id},
            {"opportunity_id": opp7.id, "skill_id": skill_data_analysis.id},
            {"opportunity_id": opp8.id, "skill_id": skill_prompt_eng.id},
            {"opportunity_id": opp8.id, "skill_id": skill_data_analysis.id},
        ])
    )

    # 8. Governance Records
    govs = [
        Governance(
            ai_opportunity_id=opp1.id,
            category="privacy",
            risk_level="low",
            description="Uses aggregated store-level historical sales; no PII involved.",
            notes="Compliance verified under retail analytics policy.",
        ),
        Governance(
            ai_opportunity_id=opp1.id,
            category="explainability",
            risk_level="medium",
            description="Demand planners must be able to understand driver feature importance.",
            notes="SHAP feature summary dashboards to be provided.",
        ),
        Governance(
            ai_opportunity_id=opp5.id,
            category="privacy",
            risk_level="high",
            description="LLM customer support agent accesses customer names, addresses, and order details.",
            notes="Strict PII masking required before passing context to external model endpoints.",
        ),
        Governance(
            ai_opportunity_id=opp5.id,
            category="human_oversight",
            risk_level="medium",
            description="Customer support copilot operates in human-in-the-loop mode for 6 months.",
            notes="Agent must click approve before any refund or email is sent to customer.",
        ),
        Governance(
            ai_opportunity_id=opp2.id,
            category="bias_fairness",
            risk_level="medium",
            description="Ensure dynamic pricing does not discriminate unfairly by neighborhood zip code.",
            notes="Fairness constraints enforced across store demographic tiers.",
        ),
        Governance(
            ai_opportunity_id=opp3.id,
            category="model_risk",
            risk_level="medium",
            description="Autonomous PO generation could over-order inventory during unexpected supplier delays.",
            notes="Max PO cap per vendor set to $50,000 without human approval.",
        ),
    ]
    session.add_all(govs)
    await session.flush()

    # 9. Transformation Initiatives
    init1 = TransformationInitiative(
        organisation_id=org.id,
        name="Enterprise AI Supply Chain Modernization",
        description="Comprehensive overhaul of demand planning, inventory allocation, and supplier replenishment using AI.",
        status="in_progress",
        department="Supply Chain Operations",
    )
    init2 = TransformationInitiative(
        organisation_id=org.id,
        name="Next-Gen Omnichannel Customer Experience",
        description="Deploying AI support copilot and real-time personalized promotional engine for digital and store shoppers.",
        status="planning",
        department="Customer Experience",
    )
    init3 = TransformationInitiative(
        organisation_id=org.id,
        name="Smart Store Operations & Computer Vision",
        description="Automating shelf auditing and fraud detection using camera vision and edge processing.",
        status="proposed",
        department="Retail Operations",
    )
    session.add_all([init1, init2, init3])
    await session.flush()

    # Link opportunities to initiatives via association table
    from sqlalchemy import insert
    from app.db.models.associations import opportunity_initiatives

    await session.execute(
        insert(opportunity_initiatives).values([
            {"opportunity_id": opp1.id, "initiative_id": init1.id},
            {"opportunity_id": opp3.id, "initiative_id": init1.id},
            {"opportunity_id": opp5.id, "initiative_id": init2.id},
            {"opportunity_id": opp8.id, "initiative_id": init2.id},
            {"opportunity_id": opp6.id, "initiative_id": init3.id},
            {"opportunity_id": opp7.id, "initiative_id": init3.id},
        ])
    )

    # 10. Dependencies
    deps = [
        Dependency(
            organisation_id=org.id,
            source_entity_type="initiative",
            source_entity_id=init2.id,
            target_entity_type="initiative",
            target_entity_id=init1.id,
            relationship_type="requires",
            description="Omnichannel CX requires accurate real-time inventory levels from Supply Chain initiative.",
        ),
        Dependency(
            organisation_id=org.id,
            source_entity_type="opportunity",
            source_entity_id=opp3.id,
            target_entity_type="opportunity",
            target_entity_id=opp1.id,
            relationship_type="requires",
            description="Automated Supplier Replenishment requires trained AI Demand Forecasting model output.",
        ),
        Dependency(
            organisation_id=org.id,
            source_entity_type="opportunity",
            source_entity_id=opp5.id,
            target_entity_type="process",
            target_entity_id=proc_cs.id,
            relationship_type="enables",
            description="Customer Support Copilot enhances Customer Support & Inquiries process response times.",
        ),
    ]
    session.add_all(deps)
    await session.commit()

    logger.info("Successfully seeded NovaMart enterprise data!")
    return org
