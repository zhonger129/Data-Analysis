## Summary

The purpose of this analysis bases on the dataset of Titanic passengers. We will make a data visualization to help us find the survival rate for the passengers. For example, it's to show the survival rate of passengers over the Age, whether male or female would have more survived people in the sinking of the Titanic.


## Design

As I shall focus on using d3.js for data visualization, but less data wrangling in this project. Therefore, I select Titanic data as my dataset of visualization. There are some passengers don't have age information in Titanic data, I use python to fill the missing age with median, and group the passengers to groups over 10 ten years.

This analysis will create a visualization that shows the passenger survival rate information between those passengers who survived and those who died, including dimensionality for overall passenger, male and female over age.

This visualization mainly compare the survival rate between the selected passengers. According the the design principles of visualization, using Bar chart for this is a good selection. Base on the feedback I collected, I add for male and female tell readers more information, I also and tooltip and legend on the graphic to help reader understand the data.


## Feedback 

* Add interaction (such as tooltip) to help reader understanding of the data.
* Except for overall passengers, it's better to have more bar to analysis for male and female.
* Add legend, X and Y axis name can help to understand the graphic.

## Resources

Udacity course
https://classroom.udacity.com/nanodegrees/nd002-cn-advanced/parts/7f46cd58-8041-4d9d-88a5-4b7c6f7be63e

SVG
https://developer.mozilla.org/en-US/docs/Web/SVG

D3.js
https://d3js.org/
