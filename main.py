import os
from typing import Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict


load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError(
        "GEMINI_API_KEY is not set. Create a .env file from .env.example "
        "and add your Gemini API key."
    )

MODEL_NAME = os.getenv("MODEL_NAME", "google_genai:gemini-3.7-flash")
llm = init_chat_model(MODEL_NAME)


class State(TypedDict, total=False):
    application: str
    experience_level: str
    skill_match: str
    response: str


def categorize_experience(state: State) -> dict:
    print("\nCategorizing the experience level of candidate...")

    prompt = ChatPromptTemplate.from_template(
        """
        Based on the following job application, categorize the candidate.

        Return ONLY one of these values:
        Entry-level
        Mid-level
        Senior-level

        Do not provide any explanation.

        Application:
        {application}
        """.strip()
    )

    chain = prompt | llm
    result = chain.invoke({"application": state["application"]})

    return {"experience_level": result.text.strip()}


def assess_skillset(state: State) -> dict:
    print("\nAssessing the skillset of candidate...")

    prompt = ChatPromptTemplate.from_template(
        """
        Based on the following job application for a Python Developer,
        assess whether the candidate's skillset matches the role.

        Return ONLY one of these values:
        Match
        No Match

        Do not provide any explanation.

        Application:
        {application}
        """.strip()
    )

    chain = prompt | llm
    result = chain.invoke({"application": state["application"]})

    return {"skill_match": result.text.strip()}


def schedule_hr_interview(state: State) -> dict:
    print("\nScheduling the interview...")
    return {"response": "Candidate has been shortlisted for an HR interview."}


def escalate_to_recruiter(state: State) -> dict:
    print("\nEscalating to recruiter...")
    return {
        "response": (
            "Candidate has senior-level experience but doesn't match the required job skills."
        )
    }


def reject_application(state: State) -> dict:
    print("\nRejecting application...")
    return {
        "response": "Candidate doesn't match the required job skills and has been rejected."
    }


def route_app(
    state: State,
) -> Literal[
    "schedule_hr_interview",
    "escalate_to_recruiter",
    "reject_application",
]:
    skill_match = state.get("skill_match", "").strip()
    experience_level = state.get("experience_level", "").strip()

    if skill_match == "Match":
        return "schedule_hr_interview"

    if experience_level == "Senior-level":
        return "escalate_to_recruiter"

    return "reject_application"


def build_graph():
    workflow = StateGraph(State)

    workflow.add_node("categorize_experience", categorize_experience)
    workflow.add_node("assess_skillset", assess_skillset)
    workflow.add_node("schedule_hr_interview", schedule_hr_interview)
    workflow.add_node("escalate_to_recruiter", escalate_to_recruiter)
    workflow.add_node("reject_application", reject_application)

    workflow.add_edge(START, "categorize_experience")
    workflow.add_edge("categorize_experience", "assess_skillset")

    workflow.add_conditional_edges(
        "assess_skillset",
        route_app,
        {
            "schedule_hr_interview": "schedule_hr_interview",
            "escalate_to_recruiter": "escalate_to_recruiter",
            "reject_application": "reject_application",
        },
    )

    workflow.add_edge("schedule_hr_interview", END)
    workflow.add_edge("escalate_to_recruiter", END)
    workflow.add_edge("reject_application", END)

    return workflow.compile()


app = build_graph()


def run_candidate_screening(application: str) -> dict:
    result = app.invoke({"application": application})

    return {
        "experience_level": result["experience_level"],
        "skill_match": result["skill_match"],
        "response": result["response"],
    }


def main():
    print("LangGraph Candidate Screening")
    print("-----------------------------")

    application = input("Enter candidate application: ").strip()

    if not application:
        print("Application cannot be empty.")
        return

    result = run_candidate_screening(application)

    print("\nComputed Results")
    print("----------------")
    print(f"Experience Level: {result['experience_level']}")
    print(f"Skill Match: {result['skill_match']}")
    print(f"Response: {result['response']}")


if __name__ == "__main__":
    main()
