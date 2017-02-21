import { Component, OnInit, Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions, URLSearchParams } from '@angular/http';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/toPromise';

declare var $: any;

@Component({
  moduleId: module.id,
  selector: 'login-selector',
  templateUrl: "login.component.html",
})

@Injectable()
export class LoginComponent implements OnInit  {
	private client_id:string = "4ca47a9bc303b55af5d2";
	private client_secret: string = "d6ff25620e4461c2655b75f994ba8dff40508430";
	private code:string = "";
	private state: string = "";

	private qs = (function(a) {
	    if (a.length == 0) return {};
	    var b = {};
	    for (var i = 0; i < a.length; ++i)
	    {
	        var p=a[i].split('=', 2);
	        if (p.length == 1)
	            b[p[0]] = "";
	        else
	            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
	    }
	    return b;
	})(window.location.search.substr(1).split('&'));
	
	constructor (private http:Http ){}
	

	ngOnInit() {
		this.code = this.qs['code'];
		this.state = this.qs['state'];

		if(this.code == undefined){
			console.log("Not yet authenticated!");
		} else {
			this.authenticate();
		}
	}

	authenticate(){
		let search = new URLSearchParams();
		search.set('code', this.code);
		search.set('client_secret', this.client_secret);
		search.set('client_id', this.client_id);
		/*
		let request_data = {};
		request_data['code'] = this.code;
		request_data['client_secret'] = this.client_secret;
		request_data['client_id'] = this.client_id;
		*/
		//let request_data_string = JSON.stringify(request_data);
		let request_data_string = search.toString();

		console.log(request_data_string);

		let headers = new Headers();
		headers.set('Content-Type', 'application/x-www-form-urlencoded');
		//headers.append("Access-Control-Allow-Origin", "*");
		//headers.append("", value: string);


		let data = this.http.post('https://github.com/login/oauth/access_token/', request_data_string, {headers}).toPromise().then((responce)=>this.checkResult(responce));
	}

	checkResult(responce: any){
		console.log(responce);
	}
}
