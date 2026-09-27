"""Bibliography, annexes and AI-use declaration."""

from __future__ import annotations

from docbuilder import Doc

REFERENCES = [
    "3Cat. (2019, 20 November). Els costos de la congestió per entrar a Barcelona: 63.000 hores "
    "i 650.000 euros diaris. https://www.3cat.cat/324/el-costos-de-la-congestio-per-entrar-a-"
    "barcelona-63000-hores-i-650000-euros-diaris/noticia/2964709/",
    "3Cat. (2024, 4 July). Trànsit admet que la xarxa viària està al límit: quines són les vies "
    "més saturades? https://www.3cat.cat/324/transit-admet-que-la-xarxa-viaria-esta-al-limit-"
    "quines-son-les-vies-mes-saturades/noticia/3301784/",
    "Ajuntament de Barcelona. (n.d.). Portal Barcelona Dades. Retrieved 4 March 2026 from "
    "https://portaldades.ajuntament.barcelona.cat/ca/estad%C3%ADstiques/akyttjn8ff",
    "Ajuntament de Barcelona. (n.d.). Seguretat viària. Retrieved 4 March 2026 from "
    "https://ajuntament.barcelona.cat/guardiaurbana/ca/seguretat-viaria",
    "Alcolea, A. (2025, 10 March). TomTom ha estudiado a las ciudades con los peores atascos y "
    "en España hay un sorprendente nombre propio: Valencia. Xataka. https://www.xataka.com/"
    "movilidad/tomtom-ha-estudiado-a-ciudades-peores-atascos-espana-hay-sorprendente-nombre-"
    "propio-valencia",
    "Ara. (2022, 20 April). Colau haurà eliminat 17 carrils de trànsit a l’Eixample el 2023. "
    "https://www.ara.cat/societat/barcelona/colau-haura-eliminat-17-carrils-transit-l-eixample-"
    "2023_1_4344588.html",
    "Ara. (2023, 19 April). Barcelona està més col·lapsada de trànsit segons 8 de cada 10 "
    "conductors. https://www.ara.cat/societat/barcelona/barcelona-mes-col-lapsada-transit-segons-"
    "8-10-conductors_1_4680071.html",
    "Barcelona Metròpolis. (2021, 30 September). Com ens movem. "
    "https://www.barcelona.cat/metropolis/ca/continguts/com-ens-movem",
    "betevé. (2022, 11 July). L’Eixample concentra un de cada tres accidents amb ferits de tot "
    "Barcelona: 1.115 només fins al juny. https://beteve.cat/mobilitat/eixample-concentra-1-cada-"
    "3-accidents-barcelona-2022/",
    "Diario Público. (2023, 24 April). El trànsit de cotxes als accessos de Barcelona baixa un "
    "11% en vuit anys. https://www.publico.es/public/transit-cotxes-als-accessos-barcelona-baixa-"
    "11-vuit-anys.html",
    "DLR. (n.d.). SUMO documentation. Retrieved 4 March 2026 from https://sumo.dlr.de/docs/index.html",
    "El Nacional. (2022, 25 October). La congestió del trànsit a Barcelona, entre les cinc grans "
    "inquietuds dels ciutadans. https://www.elnacional.cat/ca/barcelona/la-congestio-del-transit-"
    "trafic-a-barcelona-entre-les-cinc-grans-inquietuds-dels-ciutadans_905967_102.html",
    "El Periódico. (2025, 20 January). Barcelona lidera el rànquing espanyol de temps perdut en "
    "embussos: 41 hores a l’any. https://www.elperiodico.cat/ca/barcelona/20250120/barcelona-"
    "tiempo-perdido-atascos-informe-2024-113548173",
    "Emanuel, D., Zagoury, A., & Hassidim, A. (n.d.). Green Light. Google Research. Retrieved "
    "4 March 2026 from https://sites.research.google/gr/greenlight",
    "FAMA. (2024, 19 September). La guía definitiva sobre los tipos de señales de tráfico "
    "modernas. Ledtrafficlight.cn. https://www.ledtrafficlight.cn/es/the-guide-to-modern-"
    "traffic-signal-types",
    "Google. (2023, 10 October). Project Green Light’s work to reduce urban emissions using AI. "
    "https://blog.google/outreach-initiatives/sustainability/google-ai-reduce-greenhouse-"
    "emissions-project-greenlight",
    "Google. (2024, 29 July). How Google uses AI to reduce stop-and-go traffic on your route — "
    "and fight fuel emissions. https://blog.google/outreach-initiatives/sustainability/google-ai-"
    "project-greenlight",
    "Institut Ostrom Catalunya. (2023, 19 September). El peatge urbà de congestió: Anàlisi i "
    "recomanacions per a reduir la congestió del trànsit i la pol·lució de l’aire a Barcelona. "
    "https://www.institutostrom.org/2023/09/19/el-peatge-urba-de-congestio-analisi-i-"
    "recomanacions-per-a-reduir-la-congestio-del-transit-i-la-pollucio-de-laire-a-barcelona/",
    "Kleinrock, L. (1975). *Queueing Systems, Volume 1: Theory*. Wiley.",
    "López, P. A., Behrisch, M., Bieker-Walz, L., Erdmann, J., Flötteröd, Y.-P., Hilbrich, R., "
    "Lücken, L., Rummel, J., Wagner, P., & Wießner, E. (2018). Microscopic traffic simulation "
    "using SUMO. *21st IEEE International Conference on Intelligent Transportation Systems "
    "(ITSC)*, 2575–2582.",
    "Nació. (2022, 5 April). Congestió a Glòries: un embut històric que el túnel no ha "
    "solucionat. https://naciodigital.cat/societat/congestio-a-glories-un-embut-historic-que-el-"
    "tunel-no-ha-solucionat.html",
    "TomTom. (n.d.). TomTom Traffic Index. Retrieved 4 March 2026 from "
    "https://www.tomtom.com/traffic-index/about/",
    "Transportation Research Board. (2022). *Highway Capacity Manual* (7th ed.). The National "
    "Academies Press.",
    "Varaiya, P. (2013). Max pressure control of a network of signalized intersections. "
    "*Transportation Research Part C: Emerging Technologies*, 36, 177–195.",
    "Webster, F. V. (1958). *Traffic Signal Settings* (Road Research Technical Paper No. 39). "
    "Her Majesty’s Stationery Office, London.",
]


def bibliography(doc: Doc) -> None:
    doc.h("Bibliography", 1, page_break=True)
    for ref in REFERENCES:
        par = doc.p(ref, size=10, space_after=4, align="left")
        par.paragraph_format.left_indent = doc.d.styles["Normal"].paragraph_format.left_indent
        from docx.shared import Cm
        par.paragraph_format.left_indent = Cm(0.8)
        par.paragraph_format.first_line_indent = Cm(-0.8)


def annexes(doc: Doc) -> None:
    doc.h("Annexes", 1, page_break=True)
    doc.p("The annexes are published in the project repository, "
          "https://github.com/manexstako/Adaptive-traffic-signal-control, so that every "
          "result can be reproduced.")
    doc.table(["Annex", "Contents", "Location in the repository"], [
        ["1. SUMO files", "Networks and route files of both intersections",
         "`simulation/scenarios/`"],
        ["2. Python code", "Adaptive controller, baselines, experiment runner, analysis and "
         "unit tests", "`simulation/atsc/`, `simulation/*.py`, `simulation/tests/`"],
        ["3. Simulation results", "Every individual simulation (one JSON line each), "
         "parameter-tuning runs, saturation-flow measurement",
         "`simulation/results/runs.jsonl`, `tuning.jsonl`, `saturation_flow.json`"],
        ["4. Calculations", "Means, confidence intervals, paired improvements and figures",
         "`simulation/results/summary.csv`, `comparison.json`, `figures/`"],
    ], widths_cm=[3.2, 6.8, 6.0], align_numbers=False)


def ai_declaration(doc: Doc) -> None:
    doc.h("Declaration on the use of generative AI tools", 1, page_break=True)
    doc.p("Within this research project, large language models (LLMs) "
          "were used as tools for technical and methodological support, under the direct "
          "supervision of the author. The tools used were Claude (Anthropic), ChatGPT "
          "(OpenAI) and Gemini (Google). Claude was used to generate the base structure of "
          "the Python code, especially the integration with SUMO’s TraCI module; ChatGPT for "
          "debugging and optimising specific code fragments; Gemini to speed up the "
          "consultation of SUMO’s technical documentation and to cross-check data on "
          "Barcelona’s road infrastructure, whose sources were later verified manually. "
          "Text-processing capabilities were also used to polish the academic register of "
          "some sections.")
    doc.p("**English edition (2026).** For this edition, Claude (Anthropic), used through "
          "Claude Code, was used to translate the text into English and as support in reviewing "
          "and optimising the simulation code and the mathematical formulation, in running and "
          "analysing the simulations, and in drafting the text that presents the results. "
          "This work was carried out under the supervision of the author, who is responsible "
          "for the final content.")
    doc.p("**Authorship.** The original idea of the adaptive algorithm, the phase-pressure "
          "formulation, the design of the simulation scenarios and the visit to the Mobility "
          "Management Centre are the author’s own work.")
