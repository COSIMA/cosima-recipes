Notebook Guidelines
===================

For optimum presentation in the gallery, notebooks should follow a few
simple rules:

1. The first cell must be a Markdown cell containing a title
2. The first cell should include a short summary, which will be shown
   as a tooltip

By default, the chosen thumbnail is the last matplotlib figure in the
notebook. This can be changed by setting the ``thumbnail_figure`` key
in the notebook metadata to the integer index of the desired
figure. This can be done manually, in a text editor, or through the
*Edit -> Edit Notebook Metadata* menu in jupyter.

If including external images (i.e. not plots generated in the code) in
notebooks, place them in the ``images/`` directory next to the
notebook. Use the syntax ``![image caption](images/image.png)`` to
include the image in the notebook, and add ``images/image.png``
(replaced by the correct path) into the ``other_supplementary_files``
list in the notebook metadata.
