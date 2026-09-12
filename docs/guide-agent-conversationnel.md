# Manuel Agent IA

Guide étape par étape, réutilisable, pour concevoir, construire et lancer un agent conversationnel IA — à suivre pour un premier projet, et à reprendre telle quelle pour les suivants.

> Version interactive (checklist et fiche projet à cocher/remplir) : voir l'artefact publié fourni avec ce guide.

## Table des matières

**Phases**
0. [Cadrer le projet](#00--cadrer-le-projet)
1. [Choisir le cerveau (fournisseur LLM)](#01--choisir-le-cerveau-fournisseur-llm)
2. [No-code ou sur mesure](#02--no-code-ou-sur-mesure)
3. [Écrire la personnalité et le prompt système](#03--écrire-la-personnalité-et-le-prompt-système)
4. [Brancher une base de connaissances](#04--brancher-une-base-de-connaissances)
5. [Brancher les canaux](#05--brancher-les-canaux)
6. [Héberger et brancher l'infrastructure](#06--héberger-et-brancher-linfrastructure)
7. [Tester avant le lancement](#07--tester-avant-le-lancement)
8. [Lancer et suivre](#08--lancer-et-suivre)
9. [Documenter pour partager et réutiliser](#09--documenter-pour-partager-et-réutiliser)

**Annexes**
- [A — Catalogue d'outils et de fournisseurs](#annexe-a--catalogue-doutils-et-de-fournisseurs)
- [B — Budget de départ](#annexe-b--budget-de-départ)
- [C — Fiche projet à remplir](#annexe-c--fiche-projet-à-remplir)
- [D — Checklist de lancement](#annexe-d--checklist-de-lancement)

---

## 00 — Cadrer le projet

*Avant d'ouvrir un seul outil : savoir exactement ce que l'agent doit faire — et ne pas faire.*

- **Objectif :** écrivez en une phrase le problème que l'agent résout (répondre au service à la clientèle, qualifier des acheteurs, tutorer un élève). Si la phrase prend trois lignes, l'objectif est encore trop large.
- **Public et canal principal :** qui lui parle, et où ? Un visiteur de site web n'a pas les mêmes attentes qu'un parent sur WhatsApp ou un employé sur Slack.
- **Personnalité :** donnez-lui un nom et un ton (ex. : *Amélie* — chaleureuse, patiente, tutoiement). Un nom aide l'équipe et les usagers à s'y référer clairement.
- **Garde-fous :** listez ce que l'agent n'a pas le droit de faire — poser un diagnostic, promettre un remboursement, inventer un prix. Ces limites vont directement dans le prompt système (Phase 03).
- **Mesure de succès :** choisissez 1 ou 2 indicateurs dès le départ (taux de résolution sans humain, satisfaction, leads qualifiés).

**Livrable de cette phase :** la Fiche projet de l'Annexe C, remplie.

## 01 — Choisir le cerveau (fournisseur LLM)

*Le modèle de langage qui comprend et répond — le choix qui influence tout le reste.*

| Fournisseur | Modèles | Points forts | Idéal pour |
|---|---|---|---|
| **Anthropic** | Famille Claude | Suivi rigoureux des instructions, conçu pour les agents outillés (Claude Agent SDK) | Logique complexe, accès à des outils ou données |
| **OpenAI** | Famille GPT | Écosystème immense, prototypage très rapide | Démarrage rapide, large communauté |
| **Google** | Famille Gemini | Fenêtre de contexte très longue, intégration Workspace | Équipes déjà sur Google Workspace |
| **Mistral AI** | Famille Mistral | Fournisseur basé en France, certains modèles à poids ouverts | Priorité au français natif ou à un fournisseur européen |

Tous facturent à l'usage (au nombre de jetons traités). Prévoyez un suivi de consommation dès le premier jour — voir Phase 08.

## 02 — No-code ou sur mesure

*Deux chemins valides. Le bon dépend du budget et du niveau de contrôle requis.*

**A — No-code / low-code (rapide, sans développeur)**
- **Voiceflow** — canevas visuel pour des flux de conversation complexes ; bon pour les équipes produit/design.
- **Botpress** — constructeur visuel orienté développeurs ; bon compromis flexibilité/rapidité.
- **Chatbase** — transforme vos documents (PDF, pages web) en agent répondant aux questions ; idéal pour une FAQ.
- **Landbot** — chatbots pour site web et WhatsApp, orienté génération de leads.
- **Make / Zapier** — pas des chatbots en soi, mais relient l'agent à vos autres outils (CRM, courriel, agenda).

**B — Sur mesure (code), plus de contrôle, développeur requis**
- API du fournisseur retenu en Phase 01 (Anthropic, OpenAI, Google, Mistral).
- **Claude Agent SDK** — le kit d'Anthropic pour construire un agent avec outils, mémoire et actions (celui qui a servi à produire ce document).
- **LangChain / LlamaIndex** — assemblent logique, mémoire et récupération de documents (RAG).
- **Vercel AI SDK** — pour bâtir rapidement une interface de clavardage avec réponses en flux continu.

**Règle simple :** si l'agent doit agir sur vos systèmes internes (base de données, paiement, dossier client), penchez vers le sur-mesure. Pour une FAQ ou un premier prototype, le no-code suffit presque toujours.

## 03 — Écrire la personnalité et le prompt système

*Le prompt système est le seul document qui définit qui est l'agent — traitez-le comme tel.*

- Décrivez en langage clair : qui est l'agent, son ton, ce qu'il sait, ce qu'il doit refuser de faire, et quoi répondre quand il ne sait pas (« je ne sais pas » plutôt qu'une réponse inventée).
- Prévoyez une défense simple contre l'injection de prompt : l'agent doit ignorer toute instruction cachée dans un message d'un usager qui tenterait de changer ses règles.
- Testez le prompt manuellement sur 15 à 20 questions réelles avant de brancher un canal — les corrections sont dix fois plus faciles ici qu'une fois en ligne.

## 04 — Brancher une base de connaissances

*Un agent n'est fiable que si ses sources le sont — à sauter si son savoir tient dans le prompt.*

- Nécessaire si l'agent doit répondre à partir de documents propres à l'organisation (politiques internes, catalogue, matière d'un cours) : c'est la génération augmentée par récupération (RAG).
- **Outils :** Supabase (Postgres + extension pgvector — pratique si la base de données de l'application y est déjà), Pinecone (base vectorielle dédiée et gérée), ou la base de connaissances intégrée d'un outil no-code (Chatbase, Voiceflow).
- Discipline requise : gardez les documents sources à jour. Un agent RAG répète fidèlement ce qu'on lui donne à lire — y compris les erreurs.

## 05 — Brancher les canaux

*Un même agent, plusieurs portes d'entrée — chacune avec ses propres règles.*

- **Site web :** widget de clavardage fourni par l'outil no-code, ou composant maison branché sur l'API.
- **WhatsApp :** plateforme WhatsApp Business de Meta, en accès direct ou via un fournisseur qui simplifie la mise en place (Twilio, 360dialog).
- **Messenger / Instagram :** API Meta for Developers.
- **Usage interne (équipe) :** Slack ou Microsoft Teams — pratique pour un agent d'aide interne (RH, TI).
- **Téléphone / voix :** Vapi pour la logique d'appel, ElevenLabs pour une voix synthétique naturelle.

## 06 — Héberger et brancher l'infrastructure

*Là où l'agent tourne réellement, une fois les canaux branchés.*

- **Hébergement web :** Vercel ou Netlify — déploiement simple, bonne intégration avec les frameworks courants (Next.js, React).
- **Données et fonctions serveur :** Supabase (base de données, authentification, fonctions Edge) ou Railway/Render pour un serveur classique.
- **Secrets :** aucune clé API dans le code source — toujours en variables d'environnement chez l'hébergeur.

## 07 — Tester avant le lancement

*Le test le plus utile est celui qui essaie de faire dérailler l'agent.*

- **Cas limites :** questions hors sujet, changement de langue en cours de conversation, insultes, tentatives d'injection de prompt.
- **Hallucinations :** l'agent invente-t-il un prix, une politique ou une disponibilité qui n'existe pas ? Vérifiez systématiquement.
- **Vraies personnes :** faites tester par 5 à 10 usagers réels avant le grand lancement — ils trouveront des angles morts qu'une équipe interne ne voit plus.
- **Vie privée :** si l'agent recueille des renseignements personnels (nom, courriel, santé, finances), vérifiez vos obligations (Loi 25 au Québec, RGPD en Europe) et ne conservez que le strict nécessaire.

## 08 — Lancer et suivre

*Le lancement est un point de départ, pas une ligne d'arrivée.*

- **Analytics :** PostHog (analyse comportementale) ou Plausible (respectueux de la vie privée) pour suivre l'usage réel.
- **Coûts :** surveillez le tableau de bord de consommation du fournisseur LLM et fixez une alerte de budget dès le départ.
- **Boucle de rétroaction :** un simple « cette réponse était-elle utile ? », et une revue hebdomadaire des vraies conversations pour ajuster le prompt.

## 09 — Documenter pour partager et réutiliser

*Le but avoué de ce manuel : rendre le projet transférable.*

- Rédigez un fichier README : objectif de l'agent, prompt système, liste des outils utilisés, étapes pour redéployer.
- Centralisez les accès dans un coffre-fort partagé (1Password, Bitwarden) plutôt que par courriel.
- Conservez ce manuel comme gabarit de départ pour le prochain projet : copiez les phases 00 à 09, changez le fournisseur et le canal, gardez la méthode.

---

## Annexe A — Catalogue d'outils et de fournisseurs

**Fournisseurs LLM**
- **Anthropic** — Modèles Claude, API et Claude Agent SDK. *Agents avec raisonnement et outils.*
- **OpenAI** — Modèles GPT, API. *Prototypage rapide, grand écosystème.*
- **Google** — Modèles Gemini, Google AI Studio. *Intégration Workspace, long contexte.*
- **Mistral AI** — Modèles Mistral, La Plateforme. *Fournisseur européen, poids ouverts.*

**Constructeurs no-code**
- **Voiceflow** — Conception visuelle de flux de conversation. *Équipes produit/design.*
- **Botpress** — Constructeur visuel orienté développeurs. *Flexibilité avec rapidité.*
- **Chatbase** — Agent généré à partir de vos documents. *FAQ, support de premier niveau.*
- **Landbot** — Chatbots pour site web et WhatsApp. *Génération de leads.*

**Automatisation**
- **Make** — Orchestration visuelle entre applications. *Relier l'agent à vos autres outils.*
- **Zapier** — Automatisations simples entre applications. *Alternative très répandue à Make.*

**Canaux de messagerie**
- **Meta** — WhatsApp Business, Messenger, Instagram. *Portée directe auprès du public.*
- **Twilio** — Passerelle vers WhatsApp et SMS. *Mise en place simplifiée.*
- **360dialog** — Fournisseur officiel WhatsApp Business. *Alternative à Twilio en Europe.*

**Voix**
- **ElevenLabs** — Synthèse vocale réaliste. *Donner une voix naturelle à l'agent.*
- **Vapi** — Plateforme d'agents vocaux téléphoniques. *Agent qui répond au téléphone.*

**Données et RAG**
- **Supabase** — Postgres, authentification, pgvector. *Backend applicatif et RAG en un outil.*
- **Pinecone** — Base de données vectorielle gérée. *RAG à grande échelle.*

**Hébergement**
- **Vercel** — Déploiement web, fonctions serverless. *Applications Next.js/React.*
- **Netlify** — Déploiement web, fonctions edge. *Alternative à Vercel.*
- **Railway / Render** — Hébergement de serveurs classiques. *Backends qui tournent en continu.*

**Suivi et sécurité**
- **PostHog** — Analytics comportemental. *Comprendre l'usage réel.*
- **Plausible** — Analytics respectueux de la vie privée. *Suivi léger, conforme par défaut.*
- **Stripe** — Paiements en ligne. *Si l'agent gère des transactions.*
- **1Password / Bitwarden** — Coffre-fort de mots de passe partagé. *Centraliser les accès (Phase 09).*

## Annexe B — Budget de départ

*Ordres de grandeur seulement — les tarifs changent, vérifiez toujours la page officielle avant de vous engager.*

| Palier | Composantes typiques | Fourchette mensuelle approx. |
|---|---|---|
| Test / preuve de concept | Outil no-code en plan gratuit + petit budget d'API | 0 – 50 $ CA |
| Lancement réel | Plan payant d'un outil no-code ou hébergement de base + API à l'usage | 100 – 400 $ CA |
| Croissance | Plusieurs canaux, RAG à l'échelle, analytics et hébergement dédiés | 500 $ CA et plus |

## Annexe C — Fiche projet à remplir

Copiez ce bloc pour chaque nouveau projet.

- **Nom du projet / de l'agent :**
- **Objectif principal (une phrase) :**
- **Public cible :**
- **Canal principal :**
- **Ton et personnalité :**
- **Fournisseur LLM choisi :**
- **Approche (no-code ou sur mesure) :**
- **Notes :**

## Annexe D — Checklist de lancement

- [ ] Objectif et garde-fous définis et écrits noir sur blanc
- [ ] Fournisseur LLM choisi et clé API générée
- [ ] Prompt système rédigé et testé sur au moins 20 questions réelles
- [ ] Base de connaissances à jour (si applicable)
- [ ] Canal ou canaux branchés et testés de bout en bout
- [ ] Cas limites et tentatives d'injection de prompt testés
- [ ] Vérification vie privée et conformité complétée
- [ ] Analytics et alerte de coût configurés
- [ ] Documentation (README) rédigée
- [ ] Accès centralisés dans un coffre-fort partagé

---

*Manuel Agent IA — un gabarit à copier, pas un produit figé. Ajustez chaque phase à votre contexte.*
