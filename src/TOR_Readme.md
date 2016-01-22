## Tor Controller
After installing TOR on the server, it needs to have the controller turned on and accepting
authenticated connections if you are going to use the rotate ip param. Edit /etc/tor/torrc to
enable to Controller on the given port:

ControlPort 9051

and replace the token in

HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C

You can get a tor hashed password via
% tor --hash-password "my_password"
16:E600ADC1B52C80BB6022A0E999A7734571A451EB6AE50FED489B72E3DF