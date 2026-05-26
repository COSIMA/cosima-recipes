---
title: "COSIMA Cookbook: a computational learning module for analysing ocean and sea-ice model output"
tags:
  - Jupyter
  - oceanography
  - sea ice
  - computational learning
  - reproducible workflows
  - Python
authors:
  - name: Navid C. Constantinou
    orcid: 0000-0002-8149-4094
    equal-contrib: true
    affiliation: "4, 12"
  - name: Julia Neme
    orcid: 0000-0002-3573-996X
    equal-contrib: true
    affiliation: 2
  - name: Wilton Aguiar
    orcid: 0000-0003-2453-9791
    affiliation: 2
  - name: Matthis Auger
    orcid: 0000-0001-6228-5732
    affiliation: 14
  - name: Ashley J. Barnes
    orcid: 0000-0003-3165-8676
    affiliation: "4, 8"
  - name: Romain Beucher
    orcid: 0000-0003-3891-5444
    affiliation: 3
  - name: Dhruv Bhagtani
    orcid: 0000-0002-1222-375X
    affiliation: 9
  - name: Christopher Yit Sen Bull
    orcid: 0000-0001-8362-3446
    affiliation: 4
  - name: Hannah Dawson
    orcid: 0000-0001-9113-1329
    affiliation: 14
  - name: Noah Day
    orcid: 0000-0003-4176-7956
    affiliation: 12
  - name: Fabio Boeira Dias
    orcid: 0000-0002-2965-2120
    affiliation: 11
  - name: Edward Doddridge
    orcid: 0000-0002-6097-5729
    affiliation: 14
  - name: Anupiya Ellepola
    orcid: 0009-0002-8898-0068
    affiliation: 2
  - name: Matthew England
    orcid: 0000-0001-9696-2930
    affiliation: 11
  - name: Denisse Fierro-Arcos
    orcid: 0000-0002-5039-6272
    affiliation: 14
  - name: Angus Gibson
    orcid: 0000-0001-7577-3604
    affiliation: 2
  - name: Aidan Heerdegen
    orcid: 0000-0002-4481-4896
    affiliation: 3
  - name: Andy McC. Hogg
    orcid: 0000-0001-5898-7635
    affiliation: "3, 4"
  - name: Ryan M. Holmes
    orcid: 0000-0002-6799-9109
    affiliation: 5
  - name: Wilma Huneke
    orcid: 0000-0001-8624-365X
    affiliation: 2
  - name: Jemma Jeffree
    orcid: 0000-0001-7190-7329
    affiliation: "2, 4"
  - name: Andrew E. Kiss
    orcid: 0000-0001-8960-9557
    affiliation: 2
  - name: Minghang Li
    orcid: 0000-0002-6167-9999
    affiliation: 3
  - name: Josué Martínez-Moreno
    orcid: 0000-0002-8348-1588
    affiliation: 10
  - name: Jan Jaap Meijer
    orcid: 0000-0001-8667-488X
    affiliation: 14
  - name: Thomas Moore
    orcid: 0000-0003-3930-1946
    affiliation: 7
  - name: Ruth Moorman
    orcid: 0000-0001-5054-1559
    affiliation: 6
  - name: Adele Morrison
    orcid: 0009-0003-5143-5020
    affiliation: 2
  - name: James Munroe
    orcid: 0000-0001-9098-6309
    affiliation: 1
  - name: Aditya Narayanan
    orcid: 0000-0002-8967-2211
    affiliation: 13
  - name: Micael Oliveira
    orcid: 0000-0003-1364-0907
    affiliation: 3
  - name: Ellie Q. Y. Ong
    orcid: 0000-0002-0392-7915
    affiliation: "4, 8"
  - name: Max Proft
    affiliation: 3
  - name: Madelaine G. Rosevear
    orcid: 0000-0003-4254-843X
    affiliation: "4, 14"
  - name: Christina Schmidt
    orcid: 0000-0002-7672-5054
    affiliation: 10
  - name: Taimoor Sohail
    orcid: 0000-0002-4162-3269
    affiliation: 12
  - name: Paul Spence
    orcid: 0000-0001-5156-2204
    affiliation: "4, 14"
  - name: Dougal T. Squire
    orcid: 0000-0003-3271-6874
    affiliation: 3
  - name: Anton Steketee
    orcid: 0009-0002-9081-4106
    affiliation: 3
  - name: Charles Turner
    orcid: 0000-0002-3262-4972
    affiliation: 3
  - name: Felipe Vilela da Silva
    orcid: 0000-0003-1967-880X
    affiliation: 14
  - name: Marc White
    orcid: 0000-0003-3882-418X
    affiliation: 3
  - name: Luwei Yang
    orcid: 0000-0001-8570-7424
    affiliation: 2
  - name: Claire Yung
    orcid: 0000-0002-0052-7668
    affiliation: 2
  - name: Jan Zika
    orcid: 0000-0003-3462-3559
    affiliation: 11
affiliations:
  - name: 2i2c
    index: 1
  - name: Australian National University, Australia
    index: 2
  - name: "Australian National University, Australia's Climate Simulator (ACCESS-NRI), Australia"
    index: 3
  - name: Australian Research Council Centre of Excellence for the Weather of the 21st Century, Australia
    index: 4
  - name: Bureau of Meteorology, Australia
    index: 5
  - name: California Institute of Technology, USA
    index: 6
  - name: Commonwealth Scientific and Industrial Research Organisation, Australia
    index: 7
  - name: Monash University, Australia
    index: 8
  - name: Princeton University, USA
    index: 9
  - name: British Antarctic Survey, UK
    index: 10
  - name: University of New South Wales Sydney, Australia
    index: 11
  - name: University of Melbourne, Australia
    index: 12
  - name: University of Southampton, UK
    index: 13
  - name: University of Tasmania, Australia
    index: 14
date: 26 May 2026
bibliography: paper.bib

---

# Summary

The COSIMA Cookbook is an open computational learning module for analysing
ocean and sea-ice model output in Jupyter notebooks. It has been developed by
the Consortium for Ocean-Sea Ice Modelling in Australia (COSIMA; https://cosima.org.au) as a community resource for researchers, students, and practitioners working
with large gridded datasets, especially output from the ACCESS ocean-sea ice
model configuration [@kiss2020accessom2]. The repository combines introductory
tutorials with worked analysis examples, all exposed through a browsable Sphinx
documentation site (\autoref{fig:website}) and backed by a citable archived
release [@cosimaCookbook].

![The COSIMA Cookbook documentation website, showing the browsable Sphinx-based
landing page used to navigate tutorials and recipes. The live site is available
at https://cosima-recipes.readthedocs.io. \label{fig:website}](website.png)

The instructional structure is central to the project. "Cooking Lessons 101"
introduces generic skills such as loading model output, working with labelled
arrays, plotting, and interacting with shared data catalogues. These tutorials
lead into domain-focused "recipes": self-contained notebooks showing how to
perform concrete diagnostics and analyses on ocean and sea-ice datasets. The
current repository contains dozens of notebooks grouped into introductory,
advanced, and region-specific collections, giving learners an incremental path
from first contact with the data ecosystem to adaptation of full workflows for
their own science questions.

The Cookbook grew from a practical need inside the COSIMA community: the tools
used to analyse modern ocean model output are powerful, but the gap between
package-level documentation and a reproducible end-to-end workflow remains
large. Users need to understand not only Python and Jupyter
[@kluyver2016jupyter], but also how to navigate high-dimensional model output,
shared high-performance computing environments, and domain-specific analysis
conventions. The Cookbook addresses that gap by packaging reusable workflows in
the same medium in which users actually work.

# Statement of Need

Ocean and climate model analysis has a steep entry cost. New users must learn
how to find datasets, load them efficiently, interpret metadata, operate on
multi-dimensional arrays, and produce scientifically meaningful diagnostics.
General-purpose libraries such as xarray [@hoyer2017xarray] provide the
foundations for these tasks, but they do not by themselves show a learner how
to translate a research question into a robust analysis workflow for a specific
model and computing environment.

The COSIMA Cookbook fills that need with a domain-specific, openly maintained
collection of computational lessons and examples. Its contribution is not a new
analysis package; rather, it is a reusable learning resource that makes
existing scientific software, data conventions, and model output more
approachable. This aligns well with JOSE's emphasis on open educational
resources that enable computational learning through authentic practice.

Several design decisions make the Cookbook particularly useful for adoption by
other groups. First, each notebook is intended to be self-contained and
well-documented, so learners can read, run, and modify a complete workflow
without reconstructing missing context from scattered notes. Second, the
repository distinguishes tutorials from recipes. Tutorials teach transferable
skills, while recipes demonstrate how those skills combine in realistic
analysis tasks. Third, the project includes contributor guidance and notebook
review conventions that encourage new analyses to be written in a reusable and
pedagogically clear style.

This structure is valuable beyond the immediate COSIMA context. Many research
communities maintain model output on shared infrastructure and face the same
challenge: turning expert tacit knowledge into examples that newcomers can
adapt. The Cookbook offers a model for how a scientific collaboration can
capture that knowledge in version-controlled notebooks, publish it as a living
resource, and continuously improve it through community contribution.

# Educational Design and Experience of Use

The learning experience is organised as a progression. The documentation points
new users first to introductory lessons, including material on loading,
slicing, and visualising model output. Learners then move to more advanced
tutorials and finally to recipe notebooks that address concrete scientific
questions. The categories of "appetisers", "mains", and "local dishes" provide
a lightweight pedagogical cue about expected complexity and scope.

The intended mode of use is also explicit. The repository is designed around
Jupyter-based analysis on the Australian National Computational Infrastructure,
with guidance on running notebooks through ARE/JupyterLab sessions and on
accessing shared data holdings. This makes the Cookbook more than a static
collection of examples: it is operational documentation for a real analysis
environment. At the same time, the notebooks demonstrate broadly transferable
patterns for working with labelled geophysical data, so individual lessons can
be reused or adapted outside that environment.

The project also supports community authorship. Contributors are encouraged to
submit new notebooks through pull requests, document their methods clearly, and
generalise workflows so that they remain useful to others. In that sense, the
Cookbook functions both as a learning module for end users and as a framework
for teaching reproducible scientific communication through notebook design and
peer review.

# Author order

The first two authors contributed equally; authors from the third position
onward are listed alphabetically by surname.

# Acknowledgements

We acknowledge the COSIMA community for developing and maintaining the model
output, workflows, and pedagogical practices reflected in this repository. We
also acknowledge the National Computational Infrastructure, which is supported
by the Commonwealth government of Australia, and the ACCESS-NRI ecosystem that
make the operational use of these notebooks possible.
We acknowledge funding from the Australian Research Council under the Center of Excellence for the Weather of the 21st Century CE230100012, the Linkage Infrastructure, Equipment and Facilities LP200100406, and the Discovery Project DP240101274.

# References
