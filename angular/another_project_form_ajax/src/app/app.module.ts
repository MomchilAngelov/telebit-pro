import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';

import { AppComponent }  from './app.component';
import { LoginComponent } from './components/login/login.component';
import { FormComponent }  from './components/form/form.component';

@NgModule({
  imports:      [ BrowserModule, FormsModule, HttpModule ],
  declarations: [ AppComponent, FormComponent , LoginComponent],
  bootstrap:    [ AppComponent ]
})
export class AppModule {}
