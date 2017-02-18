require 'sinatra'
require 'rest-client'
require 'json'

# !!! DO NOT EVER USE HARD-CODED VALUES IN A REAL APP !!!
# Instead, set and test environment variables, like below
# if ENV['GITHUB_CLIENT_ID'] && ENV['GITHUB_CLIENT_SECRET']
#  CLIENT_ID        = ENV['GITHUB_CLIENT_ID']
#  CLIENT_SECRET    = ENV['GITHUB_CLIENT_SECRET']
# end

CLIENT_ID = "4ca47a9bc303b55af5d2"
CLIENT_SECRET = "d6ff25620e4461c2655b75f994ba8dff40508430"

get '/' do
  erb :index, :locals => {:client_id => CLIENT_ID}
end

get '/callback' do
  # get temporary GitHub code...
  session_code = request.env['rack.request.query_hash']['code']

  # ... and POST it back to GitHub
  result = RestClient.post('https://github.com/login/oauth/access_token',
                          {:client_id => CLIENT_ID,
                           :client_secret => CLIENT_SECRET,
                           :code => session_code},
                           :accept => :json)

  # extract token and granted scopes
  p result
  access_token = JSON.parse(result)['access_token']
  p access_token
  scopes = JSON.parse(result)['scope'].split(',')

  # check if we were granted user:email scope
  has_user_email_scope = scopes.include? 'user:email'

  # fetch user information
  auth_result = JSON.parse(RestClient.get('https://api.github.com/user',
                                          {:params => {:access_token => access_token},
                                           :accept => :json}))

  # if the user authorized it, fetch private emails
  if has_user_email_scope
    auth_result['private_emails'] =
      JSON.parse(RestClient.get('https://api.github.com/user/emails',
                                {:params => {:access_token => access_token},
                                 :accept => :json}))
  end

  erb :basic, :locals => auth_result
end
