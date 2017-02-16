import { Component } from '@angular/core';
import { Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions } from '@angular/http';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';

@Component({
  moduleId: module.id,
  selector: 'form-selector',
  templateUrl: "form.component.html",
})

@Injectable()
export class FormComponent  {
	private API_POINT = "https://api.github.com/users/MomchilAngelov/repos";
	private result = {};

	constructor (private http:Http ){}


	alert_magic(my_model: string){
		let data = this.http.get(this.API_POINT)
			.map(this.extractData)
			.catch(this.handleError);
		data.subscribe();
	}

	private generateArray(obj){
		console.log(obj);
		return Object.keys(obj).map((key)=>{ return obj[key]});
	}

	private extractData(res: Response) {
	    let body = res.json();
	    this.result = body;
	    console.log(body);
	    return body || { };
	}

	private handleError (error: Response | any) {
		let errMsg: string;
		if (error instanceof Response) {
			const body = error.json() || '';
			const err = body.error || JSON.stringify(body);
			errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
		} else {
			errMsg = error.message ? error.message : error.toString();
		}
		console.log("handleError: " + errMsg);
		return Observable.throw(errMsg);
	}

}
