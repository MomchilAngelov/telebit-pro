import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {appRouterProviders} from './app-routes';

import { AboutComponent }  from './components/about/aboutComponent';
import { navbarComponent }  from './components/navbar/navbarComponent';


@NgModule({
  imports:      [ BrowserModule ],
  declarations: [ navbarComponent, AboutComponent ],
  bootstrap:    [ navbarComponent, AboutComponent ],
})
export class AppModule { }
