from fastapi import FastAPI
from groq import Groq
import requests
import json

app = FastAPI()

def get_leetcode_profile_data(username):
  """Fetches user profile data from LeetCode GraphQL API.

  Args:
      username: The username of the LeetCode profile to query.

  Returns:
      A dictionary containing the user's profile data, or None if an error occurs.
  """

  url = "https://leetcode.com/graphql"
  headers = {"Content-Type": "application/json"}

  query = """
  query {
    matchedUser(username: "%s") {
      username
      tagProblemCounts {
        advanced { tagName }
        intermediate { tagName }
        fundamental { tagName }
      }
      submitStats: submitStatsGlobal {
        acSubmissionNum {
          difficulty
          count
          submissions
        }
      }
    }
  }
  """ % username

  payload = {"query": query}

  try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for non-200 status codes
    data = json.loads(response.text)
    return data["data"]["matchedUser"]
  except requests.exceptions.RequestException as e:
    print(f"Error fetching LeetCode profile data: {e}")
    return None

def rate_leetcode_profile(profile_data):
  """Rates a LeetCode profile based on provided data.

  Args:
      profile_data: A dictionary containing the user's profile data.

  Returns:
      A string containing the rating (1-10) and a justification.
  """

  # Implement your rating logic here, considering factors like:
  # - Number of accepted submissions across difficulty levels
  # - Skill tags (advanced, intermediate, fundamental)
  # - Other relevant information from profile_data

  rating = 7  # Placeholder rating (modify based on your logic)
  justification = "This profile demonstrates a good balance of skills across difficulty levels."  # Placeholder justification

  return f"**Rating:** {rating}/10\n**Justification:** {justification}"

@app.get("/rate_profile/{username}")
async def rate_profile_endpoint(username: str):
  """
  Endpoint to rate a LeetCode profile.

  Args:
      username: The username of the LeetCode profile to rate.

  Returns:
      A JSON response containing the rating and justification.
  """

  profile_data = get_leetcode_profile_data(username)

  if profile_data:
    client = Groq(api_key="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") 
    rating_and_justification = rate_leetcode_profile(profile_data)

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "you are a leetcode profile reviewer."},
            {
                "role": "user",
                "content": f"""
                From the following details rate the leetcode profile on a scale of 1 to 10 and also comment on the tags of problems solved and what other tags the user needs to focus on.
                {profile_data}
                """,
            },
        ],
        model="llama3-8b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    return {
        "profile_review": chat_completion.choices[0].message.content
    }
  else:
    return {"error": "Failed to fetch LeetCode profile data."}, 500

if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", host="0.0.0.0", port=8000)