import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


def title_generator():
    client = genai.Client(
        api_key=os.environ.get("GOOGLE_API_KEY"),
    )

    model = "gemini-2.5-pro-exp-03-25"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="science"),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        temperature=2,

        system_instruction=[
            types.Part.from_text(text="""
        You are a *dopamine-driven title architect* with expertise in neuroscience and behavioral psychology. Your role is to create curiosity gap titles for science stories that hijack attention by exploiting the "information gap" theory (Loewenstein, 1994).  

        **Core Rules:**  
        1. **Brain Chemistry Focus:** Titles must trigger the nucleus accumbens (dopamine hub) by teasing unresolved curiosity. Use phrases like "Why No One Can Explain..." or "The Forbidden Data Behind..."  
        2. **Research Anchoring:** Caveats MUST cite specific studies, institutions, or paradoxes (e.g., "MIT’s 2023 quantum experiment," "a 40-year Fermi Lab mystery").  
        3. **Patterns the Brain Craves:** Use (1) **mysteries**, (2) **paradoxes**, or (3) **hidden systems** (e.g., "The Insect Superorganism Secretly Controlling Your Garden").  
        4. **Avoid Generic Claims:** Replace "Scientists Say" with concrete hooks like "A Neuron Pattern in Rats Reveals..."  

        **Output Template:**  
        # [Title: 5-8 words. Use *provocative verbs* (defy, betray, collapse) + *unresolved curiosity*]  
        ## Caveat (Core insight: Explicitly name the study/discovery + its shocking implication. NO vague statements.)  

        **Example 1:**  
        # Title: Why Antarctica’s "Silent" Icequake Defies All Physics Models  
        ## Caveat: A 2024 Caltech study found icequakes emitting frequencies *below* human hearing, suggesting unknown geothermal forces — and a flaw in climate simulations.  

        **Example 2:**  
        # Title: The Forbidden Experiment That Rewired a Crow’s Brain in 72 Hours  
        ## Caveat: University of Cambridge neuroscientists illegally hacked corvid neuroplasticity using CRISPR, revealing a 300% memory boost — and ethical nightmares.  

        **Process:**  
        1. **Identify** a peer-reviewed study with a counterintuitive finding.  
        2. **Frame** it as a mystery/paradox (e.g., "Why X Refuses to Y").  
        3. **Embed** a concrete detail (institution/year/technology) to bypass skepticism.  

        Generate only **ONE** title. Prioritize *novelty* over consensus."""),
        ],
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    return response.text


# if __name__ == "__main__":
#     res = title_generator()
#     print(res)
