This folder contains scripts used to run most of the notebooks and confirm they are still in a working state (using pytest).

For cells in notebooks which are expected to fail, you need to add a 'skip-execution' tag which will cause the cell to be skipped in automated testing. 
To do this, select the cell and open the Property Inspector (click on the icon with two cogged wheels on the right of JupyterLab) and add a tag with the text 'skip-execution'.