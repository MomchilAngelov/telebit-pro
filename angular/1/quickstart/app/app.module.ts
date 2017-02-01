import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent }  from './app.component';
import { SwagComponent } from './swag.component'

@NgModule({
  imports:      [ BrowserModule ],
  declarations: [ AppComponent, SwagComponent ],
  bootstrap:    [ AppComponent ]
})
export class AppModule { }
