import { Component } from '@angular/core';

@Component({
  selector: 'my-app',
  template: `
  	<h1>Hello {{ name }}</h1>
    <my-app2 >Loading SwagComponent content here ...</my-app2>
  	`
})
export class AppComponent  { 
	name = "Name variable";
}
