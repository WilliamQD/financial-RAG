## TODO

1. distribution of chunk size across namespaces, 100-200, 200- 400 for example
2. rapid fuzz, minhash
3. structured output
4. test retrieval numbers for 3157, 1993, 1994
5. make graph
6. still use conference call
7. make all batches 10

## Updates

1. Retreival numebers for 3157:
1994
[conference_call] retrieved 0 / filtered 0
[10K-item1] retrieved 1 / filtered 1
[10K-item7] retrieved 0 / filtered 0
[patents] retrieved 100 / filtered 288
[wsj_frontpage] retrieved 10 / filtered 10000
1995
[conference_call] retrieved 0 / filtered 0
[10K-item1] retrieved 3 / filtered 3
[10K-item7] retrieved 0 / filtered 0
[patents] retrieved 100 / filtered 299
[wsj_frontpage] retrieved 10 / filtered 10000


2. Improve Conference call generated query

Example: Coheret, gvkey 3157, year 1994 to 2010

No conference call material:

old generated query:

example 1 (2000):
10K-item1: 1. "Coherent Inc financial performance analysis 10-K MD&A"
2. "Coherent Inc business strategy and market outlook 10-K"

10K-item7: 1. "Coherent Inc financial performance 10-K report 2023"
2. "Coherent Inc revenue growth risks and opportunities 10-K notes"

patents: 1. "Coherent Inc patent filings laser technology"
2. "Coherent Inc intellectual property optical systems"

wsj_frontpage: 1. "Coherent Inc financial performance analysis 2023"
2. "Coherent Inc market trends and growth opportunities"

example 2:
10K-item1: 1. "Coherent Inc financial performance analysis 10-K MD&A"
2. "Coherent Inc business strategy and market trends 10-K"

10K-item7: 1. "Coherent Inc financial performance 10-K report 2023"
2. "Coherent Inc revenue growth risks and opportunities 10-K notes"

patents: 1. "Coherent Inc patent filings laser technology"
2. "Coherent Inc intellectual property optical systems"

wsj_frontpage: 1. "Coherent Inc financial performance analysis 2023"
2. "Coherent Inc market trends and growth opportunities"

new generated query (2000):

10K-item1: 1. In the fiscal year 2000, how did Coherent Inc. address the challenges in the laser technology market within their MD&A section? I am particularly interested in any strategic initiatives or financial performance metrics they highlighted to navigate industry competition.

2. What insights does the fiscal year 2000 10-K filing for Coherent Inc. provide regarding their revenue growth and operational efficiency? Specifically, I am looking for details in the Business Description that outline their product offerings and market positioning during that period.

10K-item7: 1. In reviewing the 10-K Financial Notes for Coherent Inc. for the fiscal year 2000, what were the key factors that influenced the company's revenue growth during that period? Additionally, how did the company's cost structure evolve in response to market conditions and competitive pressures?

2. For the fiscal year 2000, what significant accounting policies and estimates did Coherent Inc. disclose in their 10-K Financial Notes, and how might these have impacted their reported financial results? Furthermore, were there any notable contingencies or legal proceedings mentioned that could have affected the company's financial position?

patents: 1. In the fiscal year 2000, what were the key technological innovations patented by Coherent Inc., and how did these patents contribute to their market position in the laser and optics industry? Analyzing the trends in their patent filings during this period could provide insights into their strategic focus and competitive advantages.

2. How did Coherent Inc.'s patent filings in the fiscal year 2000 reflect their research and development priorities, particularly in the areas of photonics and laser technology? A detailed examination of these patents could reveal shifts in their innovation strategy and potential impacts on future product offerings.

wsj_frontpage: 1. In the fiscal year 2000, how did Coherent Inc. navigate the challenges posed by the technology market downturn, and what strategies did they implement to maintain their competitive edge? I am particularly interested in any financial performance metrics or significant corporate decisions highlighted in the WSJ Front Page during that period.

2. What were the key developments surrounding Coherent Inc. in the fiscal year 2000, especially regarding their product innovations and market expansion efforts? I would like to explore any relevant articles from the WSJ Front Page that discuss their financial outlook and industry positioning at that time.

With conference call material:

old generated query:
example 1 (2003):
10K-item1: 1. "Coherent profitability cash flow R&D supply chain management 2003"
2. "Coherent operational excellence inventory management gross profit restructuring"

10K-item7: 1. "Coherent Inc profitability cash flow R&D supply chain management 10-K"
2. "Coherent Inc impairment charges operational excellence financial guidance 10-K"

patents: 1. "Coherent Inc profitability cash flow R&D supply chain management"
2. "Coherent Inc innovation operational excellence market leadership electro-optics"

wsj_frontpage: 1. "Coherent Inc profitability cash flow R&D supply chain management 2003"
2. "Coherent Inc operational excellence gross profit inventory management fiscal 2003"

example 2 (2007):
10K-item1: 1. "Coherent Inc profitability cash flow operational excellence R&D investment"
2. "Coherent Inc financial performance margin expansion backlog growth initiatives"

10K-item7: 1. "Coherent financial performance profitability cash flow R&D investment"
2. "Coherent operational excellence margin expansion supply chain restructuring"

patents: 1. "Coherent Inc financial performance profitability cash flow R&D investment"
2. "Coherent Inc innovation operational excellence supply chain management laser technology"

wsj_frontpage: 1. "Coherent Inc profitability cash flow R&D investment 2007 earnings conference call"
2. "Coherent Inc operational excellence margin expansion supply chain restructuring fiscal 2006"

new generated query (2007):

10K-item1: 1. In analyzing Coherent Inc's performance for fiscal year 2007, what specific operational initiatives were highlighted during the earnings results conference calls, and how did these initiatives impact the company's profitability and cash flow? I am particularly interested in understanding the management's strategies and any challenges they faced during this fiscal year.

2. For fiscal year 2007, what insights can be gathered from Coherent Inc's 10-K MD&A regarding the company's market positioning and competitive advantages in the photonics industry? I would like to explore how their financial performance and strategic decisions contributed to their growth and stability during this period.

10K-item7: 1. For the fiscal year 2007, what were the key operational initiatives and financial performance metrics highlighted by Coherent Inc. during their conference calls? I am particularly interested in understanding how these factors influenced their profitability and cash flow generation throughout the year.

2. In fiscal year 2007, how did Coherent Inc. address the challenges related to their historical stock option practices, and what impact did this have on their financial reporting? Analyzing the disclosures in the 10-K Financial Notes could provide insights into the company's governance and compliance measures during that period.

patents: 1. In fiscal year 2007, what trends can be identified in Coherent Inc.'s patent filings that may have influenced their operational performance and product development strategies? Analyzing the correlation between these patent filings and the company's financial results could provide insights into their innovation trajectory during this period.

2. How did Coherent Inc.'s patent filings in fiscal year 2007 reflect their strategic focus on emerging technologies within the photonics industry? A detailed examination of these filings may reveal the company's priorities in research and development, potentially impacting their competitive positioning in the market.

wsj_frontpage: 1. What were the key financial performance indicators for Coherent Inc. during fiscal year 2007, particularly in terms of revenue growth and profitability? I'm interested in any insights or analyses presented on the WSJ Front Page that highlight the company's operational strategies and market conditions during that year.

2. How did Coherent Inc. navigate challenges in fiscal year 2007, especially regarding their stock option practices and overall financial health? I would like to explore relevant articles from the WSJ Front Page that discuss the implications of these issues on the company's performance and investor confidence.


3. Added flow chart: FinancialLLMRetreivalFlow.pdf
4. Improved structured output slightly, added description (more realistic results), tried gt but still doesn't work
5. Ran all sample, see dropbox for csv and q distribution


## New TODO
1. Let LLM give summary of conference call + two keywords query
2. Retrieve same industry 10K
3. Improve prompt for q ratio
4. Ran 50 samples