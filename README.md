# Market Intelligence reporting
Uses HTML and CSS to design an A4 template for PDF reports. Utilizing Flask for server-side processing and Jinja2 for templating, I integrate a dictionary of Matplotlib figures and strings into the HTML file. This setup enables the generation of paginated reports. [[Sample PDF Report]](https://github.com/davidweatherstone/report_builder/raw/main/Market%20Intelligence%2C%20Cost%20Drivers%20Report%2C%20Aug-24.pdf)
  
## Situation 
Many businesses require reports on share prices, commodity prices, and industry-related indexes. 

These reports are often repetitive, typically consisting of slide decks with repeated charts and brief contextual text. From my experience creating these monthly, they can become tedious, and maintaining consistent formatting is challenging.

## Task
My goal was to enhance the visual quality of the report while streamlining the update process by automating much of the work.

## Action
I initially considered using Power BI, given my experience with it. However, since colleagues were accustomed to receiving the report as a PDF in their inbox each month, and by considering the user experience, I realized Power BI dashboards require effort from the audience to interact with the visuals—navigating pages, clicking buttons, and adjusting slicers. Although the data is valuable, I doubted most people would go through the effort.

Python seemed like a better fit. I could use Pandas for data transformation, create consistent visuals with Matplotlib, and organize the content with a Python dictionary for a Flask route, using Jinja2 to loop through it. Finally, I could print the report to PDF from the browser and distribute it via email.

### Planning
To create the report, I designed three basic pages:

1. **Title page** - Contains the title, subtitle, date, and a background image.
2. **Contents page** - Lists clickable links to each report section.
3. **Report page** - The main content, with space for 1 to 3 vertically aligned plots with contextual text or a grid for 4 or more smaller plots.

I used standard CSS for styling, primarily utilizing flexbox for the layout, with grid available for pages displaying 4 or more plots.

## Result 
The report output is consistent, with uniform chart styles and spacing. Updates are easy—each page's content is stored in a Python dictionary, with titles and plots, along with related comments, organized within it:

```python
    1: {
        "title": "Inflation",
        "images": [
            {"path": Figure(figure=create_fig(eu_inflation_tweaked_filtered)), 
             "comment": "Text space here for comments to provide context"},
            {"path": Figure(figure=create_fig(eu_inflation_yoy_tweaked)), 
             "comment": "Text space here for comments to provide context"}
        ]
    }
```

Creating new pages is as simple as adding a new item to the dictionary. While my plot function is tailored to my needs, any figure object can be passed to the Figure class.

### Limitations
This solution is tailored for a specific format — displaying a title, plots, and comments in that order. To support different layouts or more flexible page designs, the project would need to be rewritten with new CSS classes and display methods.

I used Flask primarily because of my familiarity with it. It provides an easy way to pass a variable (my contents dictionary) to a template, and to dynamically update the content with a live server during development.
