
#Sass styleguide 

## Formatting
- Always use a space after the class name and before the opening `{`.
- Properties should be entered on a new line with a space between the property and the value.
- Use 4 spaces of indent for each property.
- 

## File naming
- File names should follow the snake_case convention.

## Class naming
- Class names should follow the lowercase-hyphenated convention.
- Class names are preferred inplace of identifiers in the stylesheets.


## Mixins
- Mixins must always start with a verb.
  - Example - `make-background-class`, `set-background`
- Use 4 spaces for indentation.
- Mixins should only be used when geneating css for more than one property.


## Functions
- Use 4 spaces for indentation.


## Utility classes 
- Uitility classes are dash-cased instead of using camelCase or  snake_cased. 
- Uitility classes must begin with `sh` to avoid any confusion from bootstrap classes.
- The string after the hiphen must represent a variable in the variables file.
  - Example: `shbackground-gray`, `shfontsize-xs` 


### When should uitility classes be used. 

## Variables
- Variables must be names using dash-case instead of using camelCase or  snake_cased. 
  - Example: `clr-purple-light`
- All color valriables should be prepended with `clr` followed by the name of the followed by the variation
  - Example: `clr-purple-light`, `clr-msu-green`
