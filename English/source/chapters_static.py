"""Chapters whose content is a translation of the original Catalan thesis
(front matter, chapters 1-5, 9 and 10).  Content revised in the 2026 edition
is in chapters_model.py and chapters_results.py."""

from __future__ import annotations

from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from docbuilder import ACCENT, MUTED, Doc

IMG = Path(__file__).resolve().parent / "images"


def front_matter(doc: Doc) -> None:
    d = doc.d
    t = d.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.paragraph_format.space_before = Pt(40)
    r = t.add_run("Urban traffic optimisation")
    r.bold = True
    r.font.size = Pt(30)
    r.font.color.rgb = ACCENT
    doc.p("Design and simulation of a mathematical algorithm for adaptive traffic lights",
          align="center", size=15, color=MUTED, space_after=18)
    pic = d.add_paragraph()
    pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic.add_run().add_picture(str(IMG / "cover.png"), height=Cm(15))
    doc.p("Author: Álvaro Ayas", align="center", size=12, space_after=2)
    doc.p("Research project (Treball de Recerca), Batxillerat", align="center", size=10,
          color=MUTED, space_after=2)
    doc.p("English edition, revised September 2026",
          align="center", size=10, color=MUTED)

    doc.page_break()
    for _ in range(8):
        d.add_paragraph()
    doc.p("“Essentially, all models are wrong, but some are useful.”", align="center",
          italic=True, size=14)
    doc.p("— George E. P. Box", align="center", size=11, color=MUTED)

    doc.h("Acknowledgements", 1, page_break=True)
    doc.p("I would like to thank everyone who has accompanied me during the preparation of "
          "this research project and who, in one way or another, has made it possible.")
    doc.p("First of all, I want to thank my tutor, Néstor Martínez, for his dedication, "
          "patience and guidance throughout the whole process. His support was key to "
          "steering and developing this project with rigour and motivation.")
    doc.p("Secondly, I would like to thank my mother for her help in assessing different "
          "sections and points of the work.")
    doc.p("I would also like to thank the teachers involved for their availability and "
          "interest, and for the advice and contributions that have enriched the work and "
          "helped me grow academically.")
    doc.p("To the rest of my family, thank you for your unconditional support, for believing "
          "in me at every moment and for always being by my side, in good times and in the "
          "more difficult ones.")
    doc.p("And finally, to my friends, for always being there, for encouraging me, listening "
          "to me and helping me disconnect when I needed it most.")
    doc.p("To all of you, thank you with all my heart.")


def abstract(doc: Doc, abstract_results: str) -> None:
    doc.h("Abstract", 1, page_break=True)
    doc.p("This project explores the adaptive optimisation of urban traffic lights through a "
          "mathematical and computational approach. Its aim is to design an algorithm that "
          "decides, second by second, which phase of a traffic light should be active, "
          "according to the number of vehicles and pedestrians waiting, and to compare it "
          "objectively with the traffic lights used today.")
    doc.p("Using concepts from queueing theory, a *phase-pressure* function is formulated: the "
          "vehicle term is the time needed to clear each queue, N/(μ − λ), and the pedestrian "
          "term grows with the number of people waiting and with the waiting time of the "
          "person who has waited longest, with an extra penalty that prevents anyone from "
          "waiting indefinitely. The controller always activates the phase with the highest "
          "pressure, respecting minimum and maximum green times and safe transitions.")
    doc.p("The algorithm was implemented in the SUMO traffic simulator and compared with a "
          "fixed-time plan designed with Webster’s method and with SUMO’s actuated "
          "controller, in a simple mid-block pedestrian crossing and in a four-arm "
          "“Shibuya-type” intersection, over a range of demand levels and "
          "with repeated simulations. " + abstract_results)
    doc.p("**Keywords:** urban traffic, adaptive traffic lights, optimisation, queueing "
          "theory, SUMO, mathematical model.")


def contents(doc: Doc, entries, pages) -> None:
    doc.h("Contents", 1, page_break=True)
    doc.toc(entries, pages)


def chapter_1_2(doc: Doc) -> None:
    doc.h("1. Introduction", 1)  # the section break already starts a new page
    doc.p("Ever since I was little, mathematics has been my favourite subject. I have always "
          "liked it because it makes sense: it follows a clear logic, with reasoning behind "
          "it that guides you to understand how the world works. That is why I decided to "
          "focus my research project on this discipline.")
    doc.p("At first I did not know what topic to choose, and many possible ideas came to "
          "mind: the analysis of the ideal punch using mathematics, mathematics in music, "
          "the analysis and algorithms of the natural evolution of a population of "
          "individuals… I found all of them interesting, but none fully convinced me.")
    doc.p("It was then that my tutor suggested a topic: trying to build a traffic optimisation "
          "algorithm in order to create adaptive traffic lights that would make traffic "
          "flow more smoothly. The topic caught my attention from the first moment, and I "
          "decided there and then that it would be the subject of my research project.")
    doc.p("I chose this topic because I believe that traffic networks are, in many cases, a "
          "real problem today: they are often very slow and harm not only drivers but also "
          "pedestrians. The fact that automatic traffic lights, which change from green to "
          "red every “t” units of time without taking any variable into account (such as the "
          "number of vehicles and pedestrians), still govern traffic may be one of the main "
          "reasons for its poor optimisation and efficiency. For this reason, I set out to "
          "create an algorithm for adaptive traffic lights that change from green to red "
          "not only every “t” units of time, but also taking into account those other "
          "variables.")
    doc.p("Besides this, I also decided to dive into this topic because I thought it could be "
          "very useful for learning how artificial intelligence (AI) works, its real-world "
          "applications and how it can act as an assistant when preparing a piece of work, "
          "as well as because of my interest in programming, which has led me to obtain "
          "Python programming certificates. In addition, this project is linked to the "
          "Sustainable Development Goals (SDGs), especially SDG 11 (Sustainable cities and "
          "communities), since it seeks to improve urban mobility and reduce traffic "
          "congestion, and SDG 13 (Climate action), since optimising traffic can help "
          "reduce polluting emissions.")
    doc.p("The points I set out to address in this project are the following:")
    doc.bullets([
        "Analysis and study of the current traffic situation and of conventional traffic "
        "light systems.",
        "Development of a mathematical model for the adaptive optimisation of traffic lights.",
        "Development of a traffic simulator using SUMO (Simulation of Urban MObility), on "
        "which to implement the algorithm.",
    ], numbered=True)
    doc.p("The project has a theoretical part and a practical part. The theoretical part "
          "(chapters 3 and 4) explains and analyses the current traffic situation and "
          "conventional traffic light systems, as well as their applications today. The "
          "practical part (chapters 5 to 10) is devoted to the development of the "
          "mathematical model for adaptive traffic lights and its implementation in a "
          "traffic simulator. For this, the SUMO software is used, which makes it possible "
          "to create realistic urban simulation environments in which to assess how the "
          "algorithm works and evaluate its efficiency, comparing it with systems that use "
          "conventional traffic lights.")
    doc.p("This plan makes it possible not only to test the theoretical feasibility of the "
          "algorithm but also to obtain practical results with which to assess the possible "
          "improvement in traffic efficiency. It should be stressed that the main goal of "
          "the project is the development of the optimisation model for adaptive traffic "
          "lights. Although the results are analysed, the main purpose of that analysis is "
          "to validate how the model works.")

    doc.h("2. Objectives and hypothesis", 1)
    doc.p("Before starting the study, it is necessary to clarify exactly what its objectives "
          "are and the hypothesis on which it is based.")
    doc.p("The general objective of this project is to design and evaluate an adaptive "
          "traffic signal control system capable of optimising urban traffic flow and "
          "reducing congestion compared with traditional traffic light systems.")
    doc.p("From this general objective, the following specific objectives are set:")
    doc.bullets([
        "Develop an optimisation algorithm capable of adapting signal timings to the "
        "simulated traffic conditions.",
        "Implement, in a simulation environment (SUMO), a signalised intersection under "
        "different control schemes: fixed-time control, actuated control and adaptive "
        "control following the developed algorithm.",
        "Compare the performance of the different systems using objective metrics: mean "
        "delay, waiting times, throughput and estimated emissions, among others specified "
        "later in the project.",
        "Assess possible applications and limitations of the system in a real urban context.",
    ], numbered=True)
    doc.p("From this approach, the following main hypothesis is derived:")
    doc.note("Hypothesis",
             "An adaptive traffic light system based on a mathematical optimisation model will "
             "reduce the mean delay of the vehicles in the queues compared with conventional "
             "fixed-time systems.")


def chapter_3(doc: Doc) -> None:
    doc.h("3. Analysis of current traffic", 1, page_break=True)
    doc.p("Urban traffic is a fundamental element to consider in the functioning and layout "
          "of cities. Its correct, or incorrect, management directly affects citizens’ "
          "quality of life, road safety, the environment and the local economy, among other "
          "factors. Today, many urban areas suffer from problems derived from poor traffic "
          "management, which create flow problems that translate into congestion, delays, "
          "polluting emissions and a higher risk of accidents for both vehicles and "
          "pedestrians.")
    doc.p("It is therefore necessary to analyse in detail how traffic works today, identify "
          "the factors that affect its efficiency and understand the most common problems. "
          "This knowledge is essential in order to propose innovative alternatives, such as "
          "adaptive traffic lights, that adjust to real needs at every moment. To carry out "
          "this study with real data, and considering that each urban environment is "
          "unique, I will focus the analysis on the city of Barcelona, the largest urban "
          "centre in Catalonia.")
    doc.p("The following sections address key aspects of urban traffic: how it works, the "
          "usual problems it presents and the factors that determine how smoothly it flows.")

    doc.h("3.1 How traffic works", 2)
    doc.p("Urban traffic is the result of the interaction between vehicles and pedestrians "
          "sharing the same road network. Its organisation responds to the need to ensure, "
          "in principle, efficient and safe mobility in an environment with a variable "
          "population, where the number of journeys can vary greatly.")
    doc.h("3.1.1 Road infrastructure", 3)
    doc.p("Road infrastructure is the skeleton on which mobility takes place. It consists of "
          "different parts. The main ones are:")
    doc.bullets([
        "**Pavements (sidewalks):** generally narrow ways intended for pedestrian traffic "
        "and, in certain circumstances, for vehicles travelling at reduced speed. They are "
        "characterised by high pedestrian traffic.",
        "**Roads (or streets):** wider ways intended mainly for vehicle traffic, with less "
        "interference from pedestrians. They usually have two pavements, one on each side, "
        "connected at certain points by pedestrian crossings.",
        "**Avenues:** wide streets with several lanes in each direction, designed to absorb "
        "a high traffic flow and allow fast journeys within the city. They often have green "
        "areas and wide pavements.",
        "**Intersections:** points where two or more ways cross, whether streets or "
        "pavements. They are often regulated by traffic lights or traffic signs, and they "
        "are a critical element of traffic control; their correct management is key to "
        "ensuring that traffic works properly.",
    ])
    doc.h("3.1.2 Traffic regulations and signs", 3)
    doc.p("Traffic is always governed by a set of regulations and signs that guarantee that "
          "it works properly, in an orderly and safe way. Regulations establish rules of "
          "conduct for vehicles, while signs manage specific situations and inform drivers "
          "that a special rule applies in that area. Some examples of traffic signs are:")
    doc.bullets([
        "**Traffic lights:** control devices that regulate the passage of vehicles and "
        "pedestrians at certain intersections of the road network. Their main purpose is to "
        "guarantee safety and optimise traffic flow by alternating the right of way with "
        "coloured lights: green, amber and red. Green allows passage, amber warns of an "
        "imminent change and red requires stopping.",
        "**STOP signs:** control signs found at certain vehicle intersections. They work "
        "similarly to traffic lights, except that they normally only operate at simple "
        "street-to-street intersections. Their main purpose is to guarantee safety and "
        "an optimal traffic flow.",
    ])

    doc.h("3.2 Common urban traffic problems in Barcelona", 2)
    doc.p("Barcelona is one of the European cities with the highest traffic density, "
          "especially during rush hours. According to Barcelona City Council’s Peak-Hour "
          "Traffic Congestion Index, during the busiest hours traffic in the city can reach "
          "congestion levels, with an average of 3.9 out of 5, where 5 indicates extreme "
          "congestion.")
    doc.p("The consequences are significant: according to the TomTom Traffic Index, drivers "
          "in Barcelona lose 87 hours a year stuck in traffic jams, placing the city at the "
          "top of Spain for time lost to congestion. The problem is even more serious at the "
          "metropolitan access roads, where it is estimated that 63,000 hours are lost in "
          "tailbacks every working day, the equivalent of 15.3 million hours a year, "
          "generating, among other things, an economic cost of more than €650,000 per day.")
    doc.p("Public perception confirms this: a RACC survey reveals that 8 out of 10 drivers "
          "believe congestion has worsened in recent years, and that this affects road "
          "safety and quality of life in the city.")
    doc.p("It is also essential to point out that congestion is not only a problem of time "
          "and efficiency, but also of the environment and public health. Traffic in "
          "Barcelona is responsible for 54 % of nitrogen oxide (NOx) emissions and 40 % of "
          "suspended particles in the city. These emissions represent a health problem, "
          "increasing the risk of various respiratory and cardiovascular diseases, and add "
          "to the social costs associated with mobility.")
    doc.p("For all these reasons, implementing more efficient traffic regulation systems is "
          "key to making traffic in Barcelona more efficient in terms of time and economy, "
          "and to reducing its environmental impact and the medical consequences it can have "
          "for citizens. To implement these more efficient mechanisms, it is vital to "
          "analyse the factors that determine how smoothly traffic flows in Barcelona, since "
          "these are responsible for the problems mentioned above.")
    doc.table(["Magnitude", "Value"], [
        ["Average time lost (hours / year / driver)", "87"],
        ["Hours lost at metropolitan access roads (hours / year)", "15,300,000"],
        ["Derived economic cost (€ / day)", "650,000"],
        ["Share of the city’s NOx emissions due to road traffic (all traffic, not only "
         "congestion)", "54 %"],
        ["Share of the city’s suspended particle emissions due to road traffic", "40 %"],
    ], caption="Summary of the problems derived from traffic inefficiency in Barcelona "
               "(the original Figure 1).", widths_cm=[12, 4])

    doc.h("3.3 Factors that determine traffic flow in Barcelona", 2)
    doc.p("Traffic flow in Barcelona is influenced by a combination of structural, "
          "operational and behavioural factors that together determine the level of "
          "congestion and the efficiency of the road system. The correct functioning of these "
          "factors is key to achieving a Barcelona with smoother traffic.")
    doc.h("3.3.1 Structural factors", 3)
    doc.p("The physical structure of the city of Barcelona plays a fundamental role in the "
          "efficiency of traffic. Both geographical and urban-planning factors are analysed "
          "below.")
    doc.h("3.3.1.1 Geographical factors", 4)
    doc.p("It makes sense to start with geography, since it plays an essential role. The "
          "city of Barcelona lies on a narrow plain bounded by the Mediterranean Sea to the "
          "east and the Collserola range to the west.")
    doc.image(IMG / "fig02_barcelona_map.png", "Map of Barcelona (plan view).", 12)
    doc.p("This geographical configuration, combining sea and mountains, severely conditions "
          "mobility and urban growth. In particular, two of the ring roads that should allow "
          "fast journeys, the Ronda de Dalt and the Ronda Litoral, are directly conditioned "
          "by it. The Ronda de Dalt often becomes saturated, causing delays and congestion. "
          "However, neither widening it with more lanes nor building another, more "
          "peripheral ring road are viable solutions, since the Collserola range acts as a "
          "natural barrier and tunnelling through the mountain is not a realistic option. "
          "The same applies to the Ronda Litoral, which also suffers frequent tailbacks and "
          "has the Mediterranean Sea as its geographical limit.")
    doc.image(IMG / "fig03_barcelona_roads.png",
              "Main roads of Barcelona, showing the geographical limits to the north and "
              "south.", 12)
    doc.p("By contrast, and to understand what this means through a comparison, the other "
          "large urban centre in Spain, Madrid, presents a very different situation: located "
          "on the Central Plateau and surrounded mostly by large expanses of flat land, it "
          "has much greater freedom for urban and road expansion. This has made it possible "
          "to develop a radial road network that connects the city centre with the periphery "
          "more directly.")
    doc.image(IMG / "fig04_madrid_map.png", "Map of Madrid (plan view).", 11)
    doc.p("We can clearly see how the road network of the Spanish capital is more "
          "concentrated in the east and south-west, where there is no geographical obstacle "
          "and the network can expand. In the north-west, the El Pardo hills physically "
          "prevent road development in the same way as flat areas do, and the concentration "
          "of roads there is much lower. We can conclude that having flat land available to "
          "expand the road network is key to developing an optimal network, something "
          "Barcelona lacks.")
    doc.p("The differences in traffic flow between Madrid and Barcelona further show the "
          "importance of having land available to expand the road network:")
    doc.bullets([
        "In Barcelona, drivers lose an average of 87 hours a year in traffic jams, which "
        "translates into an average of 31 minutes and 13 seconds to travel 10 km.",
        "In Madrid, by contrast, drivers lose an average of 64 hours a year in traffic "
        "jams, and it takes an average of 24 minutes and 44 seconds to travel 10 km.",
    ])
    doc.image(IMG / "fig05_tomtom_table.png",
              "The ten Spanish cities with the most time lost per driver in traffic jams "
              "(from Xataka.com, with data from tomtom.com).", 13)
    doc.h("3.3.1.2 Urban-planning factors", 4)
    doc.p("Barcelona’s urban layout plays a key role in traffic flow, conditioning the "
          "city’s capacity to absorb daily vehicle flows. Its structure combines narrow, old "
          "streets typical of the historic centre with later planned expansion areas and "
          "large traffic axes. This creates notable differences in the capacity of the "
          "streets to absorb traffic and causes recurrent congestion points.")
    doc.p("A relevant example is the Eixample, whose ordered grid makes circulation and the "
          "distribution of vehicles easier than in older areas. According to Barcelona City "
          "Council, average daily traffic in the Eixample has fallen by 17 % over the last "
          "eight years, from 350,000 to about 285,000 vehicles a day. Even so, many streets "
          "still have bottlenecks, especially at rush hour, and approximately 16.3 % of its "
          "road network suffers from high congestion.")
    doc.image(IMG / "fig06_eixample.png", "Aerial view of the Eixample district, Barcelona.", 12)
    doc.p("Compared with the historic centre of Ciutat Vella, the old streets suffer more "
          "severe and persistent congestion because of their irregular layout and limited "
          "width. Although there are no exact flow data, the Eixample concentrates one in "
          "three accidents with injuries in the whole city, which reflects the density and "
          "complexity of its traffic.")
    doc.p("As for the major road axes, Barcelona’s ring roads (Ronda de Dalt, Ronda Litoral "
          "and Ronda del Mig) and Avinguda Diagonal act as the main corridors connecting "
          "districts and metropolitan areas. Although they were conceived to relieve inner "
          "traffic and efficiently connect the city’s access roads, they suffer constant "
          "saturation, especially at rush hour and on the stretches leading to the "
          "motorways. The coexistence of multiple modes of transport (vehicles, public "
          "transport, bicycles and pedestrians) increases the complexity of their management "
          "and makes congestion worse.")
    doc.p("Overall, urban-planning factors show that Barcelona still faces major mobility "
          "challenges. Despite well-planned road structures and recent improvements in areas "
          "such as the Eixample, the limitations of the historic centre and the saturation of "
          "the major axes mean that traffic flow is constantly conditioned by the city’s "
          "physical structure and population density.")
    doc.h("3.3.2 Operational factors", 3)
    doc.p("Apart from urban and geographical conditions, traffic efficiency in Barcelona is "
          "strongly conditioned by operational factors, that is, those related to the daily "
          "management and regulation of mobility. This management takes place through a "
          "number of traffic regulation mechanisms, which may differ depending on the area.")
    doc.h("3.3.2.1 Traffic regulation mechanisms", 4)
    doc.p("Barcelona has several traffic regulation mechanisms:")
    doc.bullets([
        "**Actuated signal control:** although Barcelona has some points with actuated "
        "signal control, its implementation is still limited and isolated, without global "
        "coordination between intersections. In most cases these systems act individually "
        "and reactively, adjusting the green, amber and red cycles only according to the "
        "vehicle flow at a specific junction. This lack of interconnection means that their "
        "overall impact on traffic flow is very limited, since changes at one intersection "
        "are often not transmitted to, or adapted by, neighbouring intersections.",
        "**Speed control systems:** the city has a network of fixed, mobile and "
        "section-control speed cameras that record vehicle speeds to ensure compliance with "
        "speed limits. These systems help reduce accidents, especially in urban areas with "
        "many pedestrians or near schools. Section cameras, in particular, calculate the "
        "average speed between two points, encouraging steadier and safer driving.",
        "**Variable message signs:** Barcelona also uses variable message panels located at "
        "strategic points of the road network. They display real-time information on "
        "traffic conditions, tailbacks, road closures, roadworks or weather incidents, and "
        "can show temporary speed limits or recommend alternative routes, improving "
        "drivers’ responsiveness and the overall efficiency of the road system.",
        "**Centralised traffic management:** all these mechanisms are coordinated from "
        "Barcelona’s Traffic Management Centre, which supervises mobility across the city. "
        "The centre receives real-time data from sensors, cameras and public transport "
        "systems and can act immediately in the event of incidents, jams or emergencies. "
        "However, the lack of an extensive and synchronised deployment of current systems "
        "limits the potential for fully adaptive urban traffic management.",
    ])
    doc.h("3.3.2.2 Points of interest", 4)
    doc.p("Across the city there are points of interest where these mechanisms may differ "
          "from other areas. A prominent example is the Glòries tunnel, an infrastructure "
          "that, despite being intended to relieve traffic, has generated new jams at the "
          "entrance to the city.")
    doc.p("**Glòries tunnel.** This tunnel, which connects Gran Via with the Besòs area, "
          "opened on 3 April 2022. Despite expectations that it would improve traffic flow, "
          "reality has been different. The long queues to enter the city from the Besòs are "
          "caused by a reduction in the number of lanes and a traffic light at the tunnel "
          "exit. More than 40,000 vehicles enter from the C-31 every day. The future use of "
          "the tunnel, now that it has been shown not to have solved the tailbacks into the "
          "Catalan capital, is uncertain. The city government has opened the door to "
          "adjusting traffic lights and has warned that it will monitor the road to prevent "
          "offences, but it does not plan bigger changes, at least for now.")
    doc.image(IMG / "fig07_glories.png", "The Glòries tunnel, Barcelona.", 12)


def chapter_4_5(doc: Doc) -> None:
    doc.h("4. Study of conventional traffic lights", 1, page_break=True)
    doc.p("Having analysed the real traffic situation in Barcelona, it can be concluded that "
          "one of the most effective ways of improving traffic flow is to optimise traffic "
          "signal systems. It is therefore necessary to study how traditional traffic lights "
          "work, their types, mathematical models and limitations. The aim is to identify "
          "the weaknesses that make these systems inefficient and to establish the "
          "requirements that an adaptive traffic light algorithm must meet.")
    doc.h("4.1 Fixed-time traffic lights", 2)
    doc.h("4.1.1 Operation", 3)
    doc.p("Fixed-time traffic lights are the ones found in most cities and towns. They work "
          "with predefined cycles and phases that repeat every certain time “t”. Put more "
          "simply, a fixed-time traffic light changes from green to red every “t” units of "
          "time. These lights have no real-time responsiveness: they operate independently "
          "of the traffic and of the specific situation, which makes them ineffective in "
          "certain traffic configurations (such as saturated roads) and can make the problem "
          "worse.")
    doc.h("4.1.2 Mathematical model", 3)
    doc.p("If a cycle has a duration C and each phase i has a duration gᵢ (green), yᵢ (amber) "
          "and rᵢ (all-red), the phase changes follow the relation:")
    doc.equation(r"C=\sum_{i=1}^{n}\left(g_i+y_i+r_i\right)")
    doc.p("where n is the number of phases of the intersection. The key feature is that gᵢ, "
          "yᵢ and rᵢ remain constant regardless of the traffic flow λ, which causes "
          "inefficiencies when demand changes.")
    doc.p("Fixed-time plans are not arbitrary, however. Traffic engineers choose C and the "
          "green times from the expected demand, and the classical method to do so is "
          "Webster’s formula (Webster, 1958). If yₖ = qₖ/s is the *flow ratio* of phase k "
          "(the flow of its busiest lane, qₖ, divided by the saturation flow s), Y = Σyₖ, and "
          "L is the total time lost in the transitions of one cycle, the cycle that "
          "minimises the average vehicle delay is approximately")
    doc.equation(r"C_0=\frac{1.5\,L+5}{1-Y},\qquad g_k=\left(C_0-L\right)\frac{y_k}{Y}")
    doc.p("This is the method used in this project to build a fair fixed-time reference "
          "(section 7.4): a well-designed fixed-time plan is the real competitor of an "
          "adaptive system, not an arbitrary one.")
    doc.h("4.2 Actuated traffic lights", 2)
    doc.h("4.2.1 Operation", 3)
    doc.p("Actuated traffic lights use detectors to adapt the duration of some phases "
          "according to the presence of vehicles and pedestrians in certain lanes and "
          "crossings. Although they are more responsive than fixed-time lights, their logic "
          "is often local: each intersection acts independently, without considering the "
          "state of neighbouring intersections or the queues forming on nearby roads.")
    doc.h("4.2.2 Mathematical model", 3)
    doc.p("In actuated traffic lights, the duration of phase Gᵢ is no longer fixed but "
          "depends on the detected vehicle flow λᵢ. It is defined within limits:")
    doc.equation(r"G_{min}\leq G_i(\lambda_i)\leq G_{max}")
    doc.p("where Gᵢ(λᵢ) is the green duration of phase i as a function of the detected flow, "
          "G_min is the minimum green time the phase must keep and G_max the maximum. A "
          "simple model is:")
    doc.equation(r"G_i(\lambda_i)=G_{min}+k\cdot\lambda_i")
    doc.p("where k is a coefficient that translates “number of vehicles detected” into "
          "“additional seconds of green”. In practice, if λᵢ = 0 (no vehicle is detected) "
          "the light stays green only for the minimum time G_min, and if λᵢ is high, Gᵢ "
          "approaches G_max to allow the queue to clear. Real actuated controllers, including "
          "the one built into SUMO, implement this idea with a *gap-out* rule: the green is "
          "extended while vehicles keep arriving at the detector with short gaps between "
          "them, and it ends when a gap longer than a threshold appears or when G_max is "
          "reached.")
    doc.h("4.2.3 Adaptive (traffic-responsive) traffic lights", 3)
    doc.p("Adaptive traffic lights change their plan according to current traffic patterns "
          "measured by sensor networks, and may use centralised algorithms to coordinate "
          "intersections. This type of traffic light makes it possible to optimise the flow "
          "more globally and to reduce delays across the whole network. Today we can find "
          "different cities and areas using this kind of signal regulation thanks, for "
          "example, to Google’s Project Green Light.")
    doc.h("4.2.3.1 Google’s Project Green Light", 4)
    doc.p("Google launched Project Green Light to help cities optimise traffic light "
          "planning and reduce the emissions caused by vehicles stopping and starting. The "
          "idea is to use aggregated mobility data (for example, driving trends that can be "
          "inferred from Google Maps) to model traffic behaviour and suggest adjustments to "
          "existing signal plans, without the need to deploy costly new hardware.")
    doc.p("**General operation:**")
    doc.bullets([
        "The parameters of existing traffic lights (cycle, green phases, coordination, etc.) "
        "are inferred by analysing movement data.",
        "Traffic patterns are analysed (how often vehicles stop and start, mean waiting "
        "times, flows between adjacent intersections) to build a local traffic model.",
        "From this model, the algorithm proposes specific recommendations: for example, "
        "adding a few seconds of green at certain times, reprogramming phases or better "
        "coordinating two intersections.",
        "Municipal engineers review the recommendations and, if they accept them, can "
        "implement them, usually within minutes, using the existing traffic control "
        "infrastructure.",
        "Finally, the impact is monitored: number of stops avoided, emission reductions, "
        "redirection of flows, etc.",
    ])
    doc.p("**Preliminary results and estimated benefits:** Google reports that at the "
          "intersections where Project Green Light has already been applied, stops can be "
          "reduced by up to 30 % and emissions by up to 10 %. The project is already active "
          "in several cities (at least 70 intersections in a dozen cities), and Google states "
          "that these interventions could save fuel and reduce emissions for tens of millions "
          "of journeys per month. A relevant feature is that Project Green Light does not "
          "require new installations: the recommendations are based on existing data and "
          "are applied with the signal infrastructure the city already has.")
    doc.p("In summary, Google’s Project Green Light represents a scalable approach to "
          "adaptive traffic based on aggregated data and artificial intelligence, without the "
          "need to deploy many new sensors. This, however, limits the true efficiency and "
          "adaptability of the system, since it does not use real-time data and therefore "
          "treats traffic as a roughly constant entity, without considering its great "
          "variability.")

    doc.h("5. Adaptive traffic lights as a solution", 1, page_break=True)
    doc.p("Given the limitations of conventional systems, an attractive way of controlling "
          "and optimising traffic flow is the use of adaptive traffic lights, as Google tries "
          "to do with Project Green Light. These devices would not only be able to react to "
          "traffic locally, but could also interact and communicate with each other, forming "
          "a coordinated network that adapts in real time to road conditions.")
    doc.p("Adaptive traffic lights are based on a set of algorithms, presented later, that "
          "combine mathematical principles fed by a constant flow of data from sensors and "
          "cameras. Thanks to this, they would be able to predict traffic patterns and act "
          "optimally according to them. Their application would allow dynamic and global "
          "management of urban mobility, where each intersection would no longer be an "
          "isolated entity but part of an adaptive web of streets and pavements. This would "
          "help reduce congestion, improve traffic flow and reduce environmental impact, "
          "leading to a better quality of life for citizens.")
    doc.h("5.1 Proposed models", 2)
    doc.p("Given the limitations of traditional signal systems, two major approaches have "
          "been developed to improve traffic management: adaptive models and intelligent "
          "models.")
    doc.h("5.1.1 Adaptive models", 3)
    doc.p("Adaptive models would represent an improvement over fixed-cycle systems. Their "
          "logic is based on sensors and detection mechanisms which, interpreted by an "
          "algorithm, make it possible to adjust the duration of the phases according to "
          "real-time traffic density. In this way, traffic lights can extend or shorten the "
          "green of a lane when an accumulation of vehicles is detected. The algorithm "
          "developed in this project belongs to this family. Its closest relative in the "
          "scientific literature is *max-pressure* control (Varaiya, 2013), which also "
          "activates, at every moment, the phase with the highest “pressure” computed from "
          "the queues.")
    doc.h("5.1.2 Intelligent models", 3)
    doc.p("Intelligent models represent a qualitative evolution over adaptive ones, since "
          "they incorporate machine-learning algorithms and advanced artificial-intelligence "
          "techniques. Thanks to this, they do not just react to the data collected by "
          "sensors and cameras, but are also able to anticipate traffic behaviour by "
          "predicting patterns and trends, based both on prior training and on historical "
          "data. In addition, these models can coordinate multiple intersections jointly, "
          "establishing an interconnected and dynamic signal network. This allows global "
          "decisions that favour traffic flow across the whole city and not only at specific "
          "points.")


def chapter_9_10(doc: Doc) -> None:
    doc.h("9. Possible future improvements", 1, page_break=True)
    doc.p("The study carried out in this project has made it possible to understand the "
          "limitations of traditional signal systems and to develop and test an algorithm "
          "for a single intersection. The results of chapter 8 also point to specific "
          "improvements of the model itself:")
    doc.bullets([
        "**Better pedestrian detection and weighting.** The pedestrian weights (β, γ, δ, "
        "T_crit) decide how the controller trades vehicle delay for pedestrian waiting. "
        "They could be made to depend on the time of day, or be expressed directly in "
        "“person-seconds” so that one person waiting counts the same on foot or in a car.",
        "**Measuring how fast each queue really moves.** The vehicle term assumes that "
        "every queue is discharged at the saturation flow μ. In the Shibuya intersection, "
        "a vehicle waiting to turn left can block a shared lane, so the queue does not move "
        "and the green is wasted; this is the most likely reason why the controller loses "
        "against the fixed-time plan at intermediate demand (section 8.3). Measuring the "
        "actual discharge of each lane during green and using it instead of μ would fix "
        "this.",
        "**Taking the cost of switching into account.** Every change of phase costs up to "
        "11 s of pedestrian clearance, amber and all-red, but the policy of section 6.3 "
        "switches as soon as another phase has slightly more pressure. A switch could be "
        "required to “pay” for the lost time, for example by switching only if the other "
        "phase’s pressure exceeds the current one by a margin.",
        "**Look-ahead instead of instant pressure.** The controller reacts to the current "
        "queues only. Estimating the arrivals of the next few seconds (from detectors placed "
        "further upstream) would let it avoid cutting a platoon of vehicles that is about "
        "to arrive.",
        "**Dedicated left-turn lanes.** In the Shibuya-type intersection most of the lost "
        "capacity comes from vehicles waiting to turn left in a shared lane. No signal "
        "timing can fully solve that; a geometric change or a protected left-turn phase "
        "would.",
    ])
    doc.h("9.1 Integration of artificial intelligence (AI)", 2)
    doc.p("One of the most promising improvements is the implementation of algorithms based "
          "on artificial intelligence, especially machine learning, as already mentioned. "
          "Unlike conventional adaptive systems, which adjust green times according to "
          "predefined rules or historical patterns, AI would allow the system to learn "
          "autonomously from real traffic conditions. By analysing data from cameras, "
          "sensors, GPS and other urban sources, a reinforcement-learning model could:")
    doc.bullets([
        "Predict the arrival of vehicles seconds in advance.",
        "Adjust the time of each phase to minimise queue formation.",
        "Optimise globally according to multiple objectives (total time, emissions, public "
        "transport priority, etc.).",
    ])
    doc.p("This evolution would mean that the system would not only react but also "
          "anticipate congestion, applying proactive regulation. Pilot projects already exist "
          "in cities such as Hangzhou (China) and Pittsburgh (USA) where average journey "
          "times have been reduced by up to 25 % thanks to such models.")
    doc.h("9.2 Expansion to networks with several types of intersection", 2)
    doc.p("The proposed algorithm has been applied to isolated intersections, but the "
          "natural next step is to extend it to a network of interconnected intersections. "
          "In this scenario, traffic lights would no longer work as independent entities but "
          "would be part of a collaborative system in which each node (intersection) shares "
          "information with its neighbours. This would allow:")
    doc.bullets([
        "Dynamic coordination between consecutive traffic lights, generating optimal green "
        "waves in real time.",
        "Redistribution of flows according to global network conditions (for example, "
        "diverting vehicles towards less congested roads).",
        "Hierarchical optimisation, with a central system managing zones (such as the "
        "Eixample or Diagonal) and local sub-levels adjusting timings to micro-conditions.",
        "In addition, the application of artificial intelligence would allow the different "
        "intersections to communicate with each other and align themselves to improve "
        "traffic flow.",
    ])
    doc.p("Implementing this model would require vehicle-to-network communication "
          "infrastructure, a centralised database and a distributed control architecture "
          "able to update the parameters of each traffic light within milliseconds.")

    doc.h("10. Visit to the Mobility Management Centre (Barcelona)", 1, page_break=True)
    doc.p("Last November, I had the opportunity to present my research project at my school. "
          "After the presentation, I sent the project to Barcelona City Council’s Mobility "
          "Management Centre, hoping that the results might have some practical application "
          "and to find out whether topics similar to my project are a current line of "
          "research.")
    doc.p("After reviewing it, Roberto Ríos, who works at the Mobility Management Centre, "
          "showed particular interest in the content of my project and expressed a wish to "
          "meet me in person. As a result, I was invited to visit the centre’s facilities, a "
          "visit that took place on 3 February 2026, accompanied by my tutor.")
    doc.p("During the meeting, I was able to talk with the professionals at the centre about "
          "how traffic is currently managed in Barcelona, explain the methodology I used in "
          "my project and discuss the feasibility of my proposals. I also had the "
          "opportunity to learn first-hand about the lines of action being carried out to "
          "improve urban mobility, as well as the challenges and strategies involved in "
          "planning and optimising the signal network.")
    doc.p("This experience has not only allowed me to value the research carried out, but "
          "has also given me a practical view of how academic knowledge can be applied to "
          "the management of the city.")
    doc.image(IMG / "fig11_cgm1.png",
              "Photograph taken at Barcelona City Council’s Mobility Management Centre.", 12)
    doc.image(IMG / "fig12_cgm2.png",
              "Photograph taken at Barcelona City Council’s Mobility Management Centre.", 12)
