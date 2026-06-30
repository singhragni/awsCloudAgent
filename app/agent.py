from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core import HumanMessage
from feedparser import parse
from dotenv import dotenv

dotenv()


model = ChatOpenAI(model_name="gpt-4.1-mini",temperature=0)


@tool
def fetch_aws_rss_feed() ->str:
    """"
    Fetch AWS Services status RSS feed and the content of the feed"""

    feed = parse("https://status.aws.amazon.com/rss/all.rss")

    # detect any network error
    if feed.bozo:
        return "Error fetching AWS RSS feed."
    
    if not feed.entries:
        return "AWS is operational RSS feed."
    
    summaries = []
    for entry in feed.entries:
        summaries.append(f"Title :{entry.title}\ndescription: {entry.description} \nlink: {entry.link}")
        return "\n".join(summaries)
    



@tool
def get_azure_status_rss()->str:
    """"
    Fetch AZURE Services status RSS feed and the content of the feed
    """
    feed = parse("https://azure.status.microsoft/en-us/status/feed")

        # detect any network error
    if feed.bozo:
        return "Error fetching AZURE RSS feed."
    
    if not feed.entries:
        return "AZURE is operational RSS feed."
    
    summaries = []
    for entry in feed.entries:
        summaries.append(f"Title :{entry.title}\ndescription: {entry.description} \nlink: {entry.link}")
        return "\n".join(summaries)




   



SYSTEM_PROMPT = """
You are a cloud and service incident monitoring AI.

You receive data ONLY from official RSS feeds.

RSS feeds may include:
- outages
- degradations
- investigations
- maintenance notices
- security advisories

DE-DUPLICATION RULES:
- Avoid repeating the same incident.
- If the title and summary are similar, treat them as duplicates.
- Ignore incidents older than 24 hours.

INCIDENT CLASSIFICATION:
- outage → Service is unavailable.
- degradation → Partial impact, latency, or regional issues.
- security → Official security advisory.
- maintenance → Planned or completed maintenance.
- normal → No active issue.

NOTIFICATION RULES:
- Notify ONLY when:
  - outage
  - degradation
  - security advisory
  - official incident update
- Send notifications via Slack and Email.
- Ignore rumors or unverified reports.

OUTPUT FORMAT (FOR Each Services):

Service: Name of the service AWS and AZURE
cloudServiceName:Name of the service AWS and AZURE
Region: if mentioned , else unknown
IncidentType: outage | degradation|security | maintenance | normal 
Severity: 1(low) - 5 (critical)
Confidence: 100%
Notify: Yes | no
Summary: Concise explanation from rss
Solution: Yes


Be conservative.
Accuracy is more important than speed.
"""



agent = create_agent(
    model=model,
    tools =[fetch_aws_rss_feed, get_azure_status_rss],
    system_prompt=SYSTEM_PROMPT
)

result = agent.invoke({
    "message" :[ HumanMessage(content= "AWS STATUS and notify me only new incidents are found")]
})

print(result["message"][-1].content)