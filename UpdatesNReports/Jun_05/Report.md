1. Checked context window for our pipeline and compare to OpenAI models
- https://colab.research.google.com/drive/1UquLboq2q06KlXV2L1l-rWpRCe2DRAN3?usp=sharing
- result: well below any models context window

2. Updated OpenAI API to use Response & Reasoning model
- linked conversation history as intended
- no temperature setting for o4-mini

3. Added financial data to Question 1 template
- Ran sample 10: 10_2025-06-05-0054.csv

## NEW TODO
1. add units: in million & percentage, employee thousand
2. remove extra phrases
3. Try different role
4. 