# Related work and the scope of the contribution

Research check on 19 November 2026. I searched for constructed-language reading comprehension, synthetic narrative question answering, unseen-language induction, artificial grammar translation, and progressive hints. I compared the task and evaluation descriptions in the following primary sources. This is a targeted search and cannot establish priority across all publications or unpublished implementations.

| Project | What already exists | Relationship to this protocol |
|---|---|---|
| [Dyna-bAbI](https://aclanthology.org/2022.starsem-1.9/) | Controlled generation of synthetic stories and questions, including compositional generalization. | Closest predecessor for the story simulator, event reasoning and exact answers. |
| [IASC](https://aclanthology.org/2026.findings-acl.1455/) | Generates conlang components and handbooks to probe metalinguistic knowledge. | Closest match for constructing a language and disclosing a grammar. |
| [SILICA](https://explcre.github.io/silica/) | Invented languages, clues, and certified checks for whether a linguistic answer is identifiable. | Closest match for checking whether the weakest clues determine a unique answer. Its target includes recognizing underdetermination. |
| [In-context translation with synchronous context-free grammars](https://arxiv.org/abs/2604.07320) | Synthetic language transduction using in-context grammatical descriptions. | Establishes precedent for controlled, automatically gradable interpretation of generated languages. |
| [ConlangBench](https://arxiv.org/abs/2608.03505) | Evaluation and training on 21 existing constructed languages. | Direct naming and subject overlap. This project generates a small language instance for each paired world. |
| [LingOly](https://papers.nips.cc/paper/2024/hash/2e43584b7d7b32fb6b2aa83b32dbbb20-Abstract-Datasets_and_Benchmarks_Track.html) | Linguistic reasoning puzzles, direct accuracy, and a no-context baseline. | Precedent for measuring how much information in the prompt contributes. |

**Finding.** These sources establish substantial precedent for every major component. Among the reviewed descriptions I found no exact match for the combination of a newly generated conlang, a paired English ownership story, independently verified answers across cumulative clue levels, and a budgeted, publicly regradable model comparison. The contribution to evaluate is the usefulness and cost of that combination. A prior-art issue or PR should link a primary source and identify the overlapping task, clues, controls, and scoring rules.
