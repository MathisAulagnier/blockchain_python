<p align="center">
  <img src="images/uqac_transparent.png" alt="Logo de l'école">
</p>

# Livrable 1 - Projet - Conception et architecture des systèmes infonuagique

8INF876 - Conception/architecture des systèmes infonuagique

**Auteurs :** 
- Aulagnier Mathis AULM12040200
- Bouchadel Maxence BOUM28050200
- Jeanjacquot Thomas JEAT29090200

**Date :** 17 février 2025

---
## Le projet

Dans ce projet, nous allons analyser les problèmes du système bancaire actuel et explorer comment la blockchain pourrait y apporter des solutions. Nous nous appuierons sur une étude approfondie des technologies existantes, en examinant leurs avantages et leurs limites. En particulier, nous nous intéresserons aux solutions développées dans le secteur financier, comme Ripple ou Diem, afin d’évaluer leur impact et leur pertinence.

Pour illustrer nos conclusions, nous développerons un prototype python simplifié d’une application de transfert de fonds basée sur la blockchain. Cette maquette permettra de montrer concrètement comment une transaction peut être réalisée de manière sécurisée, rapide et transparente, sans passer par un intermédiaire bancaire. Elle servira avant tout de support démonstratif pour mieux comprendre les mécanismes et les bénéfices de la blockchain appliquée aux services financiers.

---

## Objectif du livrable 

Ce livrable vise à poser les fondations du projet en:
1. **Clarifiant le problème** : Comprendre les limites du système bancaire actuel pour mieux justifier le besoin d'une solution basée sur la blockchain.
2. **Définissant le cadre de la solution proposée** : Montrer comment la blockchain, par sa nature décentralisée et sécurisée, peut répondre aux problématiques identifiées.

Nous avons ainsi recherché des problématiques existantes suscitant notre intérêt, ce qui nous a naturellement conduits à explorer la blockchain. En nous interrogeant sur les défis que cette technologie peut résoudre, nous nous sommes penchés sur les dysfonctionnements du système bancaire.

---

### 1. Quel est le problème dans le système bancaire actuel ?

**Problèmes constatés dans le système bancaire :**

- **Centralisation et manque de transparence :**  
  Les systèmes bancaires sont hautement centralisés. Cela signifie qu’un petit nombre d’institutions détiennent et contrôlent l’ensemble des transactions et des données financières, ce qui peut limiter la transparence et accroître le risque d’erreurs ou de fraudes. 

🔹 *Exemple : Au Salvador, avant l’adoption du Bitcoin comme monnaie légale en 2021, le système bancaire traditionnel était critiqué pour son manque de transparence et son lien avec la corruption. La blockchain a été perçue comme une solution potentielle pour garantir des transactions plus ouvertes et traçables.*


- **Coûts élevés et délais de traitement :**  
  Le recours à des intermédiaires entraîne des coûts importants et des délais de traitement parfois prolongés, particulièrement pour les transactions transfrontalières.

🔹 *Exemple 1 : Un simple virement bancaire entre un compte français et un compte canadien entraîne des frais fixes de 15 $, auxquels s’ajoutent un délai de traitement pouvant aller jusqu’à plusieurs jours et un taux de change souvent désavantageux ainsi que d'autres frais appliqués par la banque. Ces coûts et délais rendent les transactions internationales peu accessibles et inefficaces pour les particuliers comme pour les entreprises.*

🔹 *Exemple 2 : Lorsque vous payez un achat par carte bancaire, des frais sont prélevés sur chaque transaction par les banques et les réseaux de paiement (Visa, Mastercard). Ces coûts sont répercutés sur les commerçants, qui les intègrent dans leurs prix. À grande échelle, cela représente des milliards d’euros captés par les intermédiaires financiers.*


- **Sécurité et vulnérabilités :**  
  La centralisation peut également rendre les systèmes bancaires vulnérables aux cyberattaques. La gestion des informations sensibles par une entité unique peut poser des défis majeurs en termes de protection des données.

🔹 *Exemple : En 2019, Capital One, une grande banque américaine, a subi une cyberattaque ayant exposé les données personnelles de 106 millions de clients. Ce type de faille met en évidence les risques liés à la centralisation des informations sensibles.*


- **Manque d’inclusion financière :**  
  Le modèle traditionnel peut exclure certaines populations ou zones géographiques, empêchant ainsi l’accès universel aux services financiers.

🔹 *Exemple : En 2010, le fondateur de WikiLeaks, Julian Assange, a vu ses comptes bancaires bloqués par plusieurs institutions financières sous pression des gouvernements. En réponse, WikiLeaks a commencé à accepter des donations en Bitcoin, démontrant l’utilité des cryptomonnaies pour contourner la censure financière.*

Ces lacunes montrent clairement l’intérêt d’explorer des approches alternatives pour améliorer la rapidité, la sécurité, et l’accessibilité des services financiers.

---

### 2. Comment allons-nous procéder pour intégrer la blockchain comme solution ?

**Notre démarche se décompose en plusieurs étapes :**

1. **État de l’art et bibliographie :**  
   - *Origine et concepts fondamentaux :*  
     Nous débuterons par l’analyse des travaux pionniers sur l’horodatage des documents numériques, par exemple l’article célèbre de Haber et Stornetta qui introduit les premières méthodes de « timestamping ». Ces travaux ont directement inspiré les fondements de la blockchain, qui vise à offrir une preuve d’immutabilité et de l’authenticité des données.
   
   - *Projets liés au domaine bancaire :*  
     Nous présenterons également des études de cas et des projets concrets existants dans le secteur financier :
       - **Le projet Libra (maintenant Diem) :**  
         Initié par Facebook (Meta), ce projet vise à créer une monnaie stable et accessible à l’échelle globale, en tirant parti des technologies décentralisées pour réduire les coûts et les délais de transaction.
       - **Le projet Ripple :**  
         Conçu pour les paiements transfrontaliers, Ripple utilise un registre distribué pour fournir des transactions rapides et sécurisées, tout en limitant les coûts associés aux conversions et aux intermédiaires.

   Ces références permettent de cadrer notre approche dans un contexte bien défini et de montrer la pertinence de la blockchain comme solution aux problèmes bancaires traditionnels.

2. **Conception et prototype technique :**
   - *Compréhension approfondie de la blockchain :*  
     Nous mettrons en lumière notre compréhension du fonctionnement de la blockchain, incluant des concepts tels que la décentralisation, l’immutabilité, le consensus distribué, et la preuve de travail.

   - *Développement d’une maquette :*  
     Nous concevrons une maquette d’une blockchain en Python. Cette maquette permettra de simuler un enregistrement sécurisé de transactions financières, montrant comment chaque transaction est horodatée et inscrite de manière immuable dans un bloc. Ce prototype servira à illustrer concrètement comment la blockchain peut résoudre certaines lacunes du système bancaire en renforçant la transparence, la sécurité, la réduction des coûts, et l’efficacité des paiements.


