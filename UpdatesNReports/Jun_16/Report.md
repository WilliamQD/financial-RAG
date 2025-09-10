## TODO:
1. Try reranker
2. Fine-tune


## Updates
2025-06-12-1355_10
- added q_tot to financial data, corr around 0.5 / 0.6

2025-06-14-1439_10
- added reranker, wrose performance, could be due to top_n = top_k // 2
- 0.2 / 0.3 

2025-06-15-2341_10
- removed reranker, tried developer msg and financial-services reasoning model role, changed to o4-mini
- re-engineered Q2 questions to make them shorter -> worse performance
- 0.4 corr, but very high q

2025-06-16-0029_10
- changed back to o3-mini
- added back "can be larger than market value"
- ~0.5 corr, normal q

2025-06-16-0121_10
- removed q_tot, 0.2 to 0.3 mean and median corr, good summary (negative q1 skewness)

2025-06-16-1018_10
- added high_q example (2.0), negative correlation around 0.1, boosted q to 1.3