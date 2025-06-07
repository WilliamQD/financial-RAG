## Updates:
### Areas to think about
1. Lack of low-q projects: likely bias to suggest "good" projects
2. insufficient variance: llm is conservative in picking values -> try higher temperature
3. overly optimistic: llm, which mimics human judgements, overly estimates benefits and underestimates costs

### Possible fixes (prompting):
1. propose one consevative project with limited upside (so chance of loss), one moderate project, one high-risk, high-rewards project
2. Include company baseline & real data like company revenue, R&D budge, market vcaptialization, typical porject costs.
"Ensure that cost and value estimates are plausible given the company’s size and industry economics." 
- zero-shot vs few-shot prompting
3. Change structure output to chain-of-thought reasoning (bascially formalize our prompting procedure). Reduce chance of arbitary guessing
4. Refine tobin's q instruction. “Tobin’s q = market value / cost. A project with q > 1 creates value; q < 1 means the investment isn’t fully justified by market value (which can happen, for example, in defensive or strategic projects). Provide market value and cost for each project (the q ratio will be calculated).”
5. Few shot prompt to show model high quality answers
6. Tweak the confidence interval -> “For each project, also estimate a confidence or probability of success.” 
Model might assign lower EV if the probability of success is low.

### Possible fixes 2:
1. Higher temperature > 1.0
2. Top-k sampling for q (or market value). generate 10 qs with distribution and sample from them (this is just top-p, apparently no need if change temp)


100_2025-06-01-1522:
1. mean: 1.08, median: 1.2, std: 0.24
2. Added tobin's q in structured output in Q2
3. really bad predictions for q1 for some reason


100_2025-06-01-1731
1. mean: 1.91, median: 1.63, std: 0.992
2. changed model to o4-mini, which has default temp = 1.0
3. Tried new prompt with three non "best" projects. New prompt kept the q distribution line
4. removed tobin's q in strucuted output

Want to try next:
1. Few-shot example
2. Chain-of-thoughts
3. Improve some OpenAI codes. o4-mini is a better reasoning model. 4.1 is not a reasoning model but will benefit from chain-of-thoughts.
- new API: https://platform.openai.com/docs/guides/text?api-mode=responses
- identity, insturctions, examples
- Reasoning model explained: https://platform.openai.com/docs/guides/reasoning?api-mode=responses&example=research
4. https://cookbook.openai.com/examples/gpt4-1_prompting_guide 
- GPT-4.1 is highly steerable and responsive to well-specified prompts - if model behavior is different from what you expect, a single sentence firmly and unequivocally clarifying your desired behavior is almost always sufficient to steer the model on course.
5. add extra stage behind structure output so it doesn't adversely affect the results.


## New TODO
1. System Role
2. Add company specific information to prompt
3. change llm workflow (create to append)
4. update API