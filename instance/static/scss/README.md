# MSU Digital Repository SCSS styleguide 

## Class naming
- Class names should follow the lowercase-hyphenated convention.
- Class names are preferred inplace of identifiers in the stylesheets.
- Class names specific to the repository must begin with `sh-`.
  - Example: `sh-example-class`, `sh-custom-class`

## File naming
- File names should follow the snake_case convention.

## Strings
- Strings should be quoted with single quotes `'`
```
// Example calling a mixin
@include do-my-mixin('passed string');
```

## Formatting
- Use 4 spaces for indentation.
- Always use a space after the class name and before the opening `{`.
- Properties should have a space between the property and the value.
- List all standard property elements before the include statements.
- Nested properties must be separated by a blank line.
- When using nested selectors do not nest more than 3 levels deep. 
```
.sh-search-btn {
    background: rgba(255,255,255, 0.9);
    color: $clr-white;
    @include set-borders($clr-white, 0, 0, 10rem, 10rem, 0);

    p {
        color: $clr-green;
    }
}
```

## Mixins
- Mixins must always start with a verb.
  - Example - `make-background-class`, `set-background`
- Mixins should only be used when geneating css for more than one property.
- All mixins must haave doc strings with verbose text explaining the purpose and parameters.
  - Example doc string for mixins
  ```
    // generates the css for the utility class that sets the font color
    //
    // @params {String} $utility-class: name of the utility class 
    //                  Example: sh-color-white
    //                  "sh-color" is the prefix and "white" is the key from $colors map in 'variables.css'
    // return value: class with css color property

  ````

## Structure
- SCSS files should be split into sepearate files based on logical organization or purpose.
- Include statements should be in alphabetical order, unless dependencies require it (must be noted in comments).
```
// Default import (must be imported first)
@import 'defaults';

// Page imports
@import 'buttons';
@import 'dropdowns';
@import 'expand';
```

## Utility classes
- Class naming should be in the format of `sh-PROPERTY-VARNAME`
  - Where `PROPERTY` is the CSS property, such as `background`
  - Where `VARNAME` is a map key defined in the variables.scss file, such as `msu-green`
  - Example: `sh-background-gray`, `sh-font-size-xs` 
- Utility classes only need to be defined when there are at least two immediate uses for it.
- Uitility classes must be included in the primary `.scss` file. Example:
```
@include make-background-class(sh-background-green-msu)
```

## Variables
- Variables must be names using dash-case in similar format to CSS class names.
  - Example: `clr-purple-light`
- All color variables should be prepended with `clr` followed by the name of the followed by the variation
  - Example: `clr-purple-light`, `clr-green-msu`
- Variables names should be defined in scope of most-broad to most-narrow, left to right.
  - Example: `clr` is most broad, `clr-green` is more narrow scope, `clr-green-msu` is the most narrow scope.
- All variable maps must use varibales for values if they have associated variabled defined elsewhere.
  - Example:
```
$colors: (
    "purple-dark": $clr-purple-dark,
    "purple": $clr-purple,
    "purple-light": $clr-purple-light,
    "green-msu": $clr-green-msu,
    "green": $clr-green,
    "green-light": $clr-green-light,
    "gray-dark": $clr-gray-dark,
    "gray": $clr-gray,
    "white": $clr-white,
    "none": $clr-none,
);
```
