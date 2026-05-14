-- 014: Fix OpenClaw agent tech_stack (was "Python + Rust + TensorFlow Lite", should be TypeScript)
UPDATE config_data
SET data = jsonb_set(data::jsonb, '{agents,openclaw,tech_stack}', '"TypeScript + Node.js + V8引擎"', false)
WHERE category = 'sillyfu' AND name = 'product'
  AND data::jsonb #>> '{agents,openclaw,tech_stack}' = 'Python + Rust + TensorFlow Lite';
