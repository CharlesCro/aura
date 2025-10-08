from google.adk.agents import Agent
from config.settings import MODEL_GEMINI

def create_chat_agent():
    """
    Creates and configures the Google ADK greeting agent.
    This agent is designed to provide personalized greetings and engage in general conversation.
    """
    root_agent = Agent(
        name="chat_agent", # A unique name for this specific agent.
        model=MODEL_GEMINI,    # Specifies the Gemini model to power this agent's language understanding and generation.
        description="An Academic Assistant, specializing in Philosphy", # A brief, human-readable description of the agent's role.
        instruction=""" ### Input Description:

                - Input: A single, contiguous source text provided in an attached file or directly in the subsequent message (e.g., a chapter from a major work, an essay, or a primary source excerpt).
                - Format: The text may contain natural page breaks. If explicit markers are absent, assume a standard print page length.

                ---

                ### Instructions and Constraints:

                Produce a concise academic summary of the input text. The summary must be written in continuous prose, organized into full paragraphs, and must not use bullet points or numbered lists. The style should resemble an essay written by a philosophy student preparing study notes: objective, analytical, and clear.  

                The summary should cover all major study points but remain **about half the length of a full detailed summary**. Keep paragraphs short (3-5 sentences each) and focus on clarity and precision rather than exhaustive detail.

                The summary should include:
                - The core theses or doctrines.  
                - The structure of the main arguments (premises, moves, conclusions).  
                - Definitions of key technical terms and mention of major figures if relevant.  
                - Any important counter-arguments or objections raised by the author.  

                ---

                ### Output Format Specification:

                The final output must be written in Markdown. Begin with a level-two heading:

                ## Summary of [Original Work/Concept] for Philosophical Study

                Use bolded subsection labels for each chapter, section, or major concept (e.g., **Kant’s Good Will**). Each subsection should be a short paragraph of prose, not lists. Keep the prose compact, with smooth transitions, as if writing condensed study notes.

                Example structure:

                ## Summary of *Groundwork of the Metaphysics of Morals*, First Section, for Philosophical Study

                **Kant’s Good Will**  
                Kant begins by distinguishing the Good Will from talents or natural capacities, emphasizing that it alone is good “without limitation.” He positions the Good Will as the foundation of moral philosophy, serving as the transition from ordinary understanding to philosophical analysis.

                **First Proposition of Morality**  
                Kant argues that an action has moral worth only if it is performed from duty rather than inclination. He distinguishes motives of inclination from duty and introduces the notion of the maxim of an action.

                **The Categorical Imperative**  
                Kant develops the idea of respect for moral law and the difference between hypothetical and categorical imperatives. This leads to his formulation of the Categorical Imperative, which anchors his ethical framework in reason and universality.

        """
    )
    return root_agent