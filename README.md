Projet prison_management avec base de donnée sqlite et django, il y'as des magistrats, des agents de prison, et des detenus de sexe opposés. 
les prison dont identifiées par nom de de ville, le gabon ayant neuf grande villes. ces prisons doivent etre interconnectées entre elles. 
de ce fait lorsqu'un magistrat délivre un mandat de dépôt, document en pdf, 
le prisonnier est incarceré et enregistré avec un numéro au service social puis à l'identification et ensuite dans sa céllule. 
nous auront la gestion des garde pour les agents de la prison pour chaque semaine. les agents auront des roles y compris les magistrat au niveau de l'application. 
je souhaiterai que le transfert des prisonnier se face avec la fonction drag drop. le gabon ayant 9 provinces, chaque prison a le nom de la province.
et que les visites des prisoniers soit vue sous forme de diagramme relationel en forme de bulles. pour chaque prisonnier enregitré, 
une notification en temps réel vers les agents et magistrats. on va ajouter des fonctionalité après et au fur et a mesure.
je le souhaite mais aussi je souhaiterai qu'on y ajouter bootstrap et l'impression de document de sortie de prison pour chatque prisonnier 
et des taches gantts linéaires pour observer le temps déja mis par chaque prisonnier.integre bootstrap4 et 5 au projet, double authentification, impression des certificats de mise en liberté pour les detenu avec photo,
enregistrement des mandat de depot en forme de pdf pour chaque detenus, les notifications de mise en liberté et le suivit du procès.utilisation vis.js pour observer les visites liés aux prisoniers dans chaque prison sous forme de reseau
le projet a déja été créé de manière partielle mais touts les fonctionalitées sont fonctionelles.

**Fonctionnalités principales**
1. **Gestion des détenus**
    - Enregistrement des nouveaux détenus par les agents
    - Suivi des transferts entre prisons
    - Gestion des dates d'incarcération et de libération
    - Historique des mouvements
    - Fiche détaillée par détenu
	- Notifications aux magistrats et agents.
	- Detection de recidivisme
	- etat de santé du detenu à l'arrivé
	- motif d'incarceration
	- gestion de recidivisme
  - photo des detenus
 - générer les matricule des detenus
 - Gestion d'accès et autorisations
 - suivit d'instruction par les magistrats etc...

2. **Gestion des procès**
    - Planification des audiences
    - Enregistrement des verdicts
    - Calcul automatique des dates de libération
    - Suivi des appels

3. **Diagramme de Gantt**
    - Visualisation des périodes de détention
    - Filtres par prison, par magistrat
    - Timeline interactive

  4. **Sécurité** :

- Authentification à deux facteurs pour les magistrats et agents
- Chiffrement des données sensibles
- Journalisation des accès
- Gestion fine des permissions

5. **Interface utilisateur** :

- Dashboard adaptatif
- Filtres avancés
- photo de profile
- Export de rapports
- Notifications pour les dates importantes
- Notifications aux Agents et magistrats
- Gestion administratif pour les agents
- Programmation des gardes, groupes et equipes
- schedules organisés
