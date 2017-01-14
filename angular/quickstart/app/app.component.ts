import { Component } from '@angular/core';
@Component({
  selector: 'my-app',
    
  moduleId: module.id,
  styleUrls: ["./app.component.css"],

  template: `
    <h1>{{title}}</h1>
    <nav>
      <a routerLink="/dashboard">Dashboard</a>
      <a routerLink="/heroes">Heroes</a>
    </nav>
    <router-outlet></router-outlet>
  `
})
export class AppComponent {
  title = 'Heroes of the Scourge';
}