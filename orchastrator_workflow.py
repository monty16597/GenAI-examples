import asyncio
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from typing_extensions import Annotated, TypedDict
import operator


class CompletedTask(TypedDict):
    description: str | None
    completed: bool = False


class Task(TypedDict):
    description: str = None
    agent_name: str = None


class SynthesizedOutput(TypedDict):
    description: str | None
    synthesized: bool = False


class State(TypedDict):
    main_query: str
    planned_task: list[Task] = []
    orchestrated_tasks: list[Task] = []
    completed_tasks: Annotated[list[CompletedTask], operator.add]
    final_output: SynthesizedOutput | None


class SubState(TypedDict):
    current_task: Task | None
    completed_tasks: Annotated[list[CompletedTask], operator.add]


async def planner(state: State):
    return {"planned_task": [{"description": "Task 1"}, {"description": "Task 2"}]}


async def orchestrator(state: State):
    tasks = []
    for task in state["planned_task"]:
        if "task 1" in task["description"].lower():
            task["agent_name"] = "worker_1"
            tasks.append(task)
        elif "task 2" in task["description"].lower():
            task["agent_name"] = "worker_2"
            tasks.append(task)
        else:
            task["agent_name"] = "END"
            tasks.append(task)
    return {"orchestrated_tasks": tasks}


async def assign_tasks(state: State):
    assignments = []
    for task in state["orchestrated_tasks"]:
        data = {"description": task["description"]}
        if task["agent_name"] == "worker_1":
            assignments.append(Send("worker_1", {"current_task": data}))
        elif task["agent_name"] == "worker_2":
            assignments.append(Send("worker_2", {"current_task": data}))
    return assignments


async def worker_1(state: SubState):
    print("Worker 1 working on: ", state["current_task"])
    return {"completed_tasks": [CompletedTask(description="Task 1 created", completed=True)]}


async def worker_2(state: SubState):
    print("Worker 2 working on: ", state["current_task"])
    return {"completed_tasks": [CompletedTask(description="Task 2 created", completed=True)]}


async def synthesizer(state: State):
    state["final_output"] = SynthesizedOutput(description="Task 1 and Task 2 created", synthesized=True)
    return state

workflow = StateGraph(State)
workflow.add_node("planner", planner)
workflow.add_node("orchestrator", orchestrator)
workflow.add_node("worker_1", worker_1)
workflow.add_node("worker_2", worker_2)
workflow.add_node("synthesizer", synthesizer)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "orchestrator")
workflow.add_conditional_edges(
    "orchestrator",
    assign_tasks,
    {
        "worker_1": "worker_1",
        "worker_2": "worker_2",
    }
)
workflow.add_edge("worker_1", "synthesizer")
workflow.add_edge("worker_2", "synthesizer")
workflow.add_edge("synthesizer", END)

app = workflow.compile()

png_bytes = app.get_graph().draw_mermaid_png()
# Write to file
with open("graph.png", "wb") as f:
    f.write(png_bytes)


async def main():
    result = await app.ainvoke({"main_query": "Create S3 bucket and Lambda function. Triggered Lambda by S3 event."})
    print(result)

asyncio.run(main())
