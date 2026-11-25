# Chain-of-Thought Reasoning & Domain Knowledge Specification

## Purpose
Defines Layer 3 (`src/layer3_reasoning/price_action_kb.py` and `cot_planner.py`) curated price-action knowledge retrieval and structured Chain-of-Thought (CoT) reasoning decoupled from arithmetic calculation.

## Requirements

### Requirement: Curated Price Action Knowledge Base
`PriceActionKnowledgeBase.RULES` SHALL provide structured domain rules covering `SR_FLIP`, `SPRING_FALSE_BREAKOUT`, `UPTHRUST_FALSE_BREAKOUT`, and `PRE_BREAKOUT_BUILDUP`.

#### Scenario: Retrieve rule summaries for prompt injection
- **WHEN** `PriceActionKnowledgeBase.get_rule_summary()` is called
- **THEN** it returns formatted summaries for all four curated Price Action rule entries

### Requirement: Decoupled Four-Step Chain-of-Thought Reasoning
`CoTPlanningAgent` SHALL generate a structured 4-step CoT reasoning payload from Layer 2 JSON geometry and ML probability inputs without modifying numerical coordinates or performing position-sizing arithmetic.

#### Scenario: Generate 4-step CoT audit narrative
- **WHEN** `CoTPlanningAgent.generate_cot_reasoning(geometry_data, ml_data)` is executed
- **THEN** the output dictionary contains `market_regime`, `chain_of_thought` (with exactly 4 reasoning steps), `liquidity_narrative`, `structural_invalidation`, and `human_readable_summary`
- **AND** `build_structured_prompt` explicitly instructs the LLM never to alter geometric coordinates
