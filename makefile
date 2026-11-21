init:
	@if [ ! -f services/identity-service/.env ]; then \
		cp services/identity-service/.env.example services/identity-service/.env; \
	fi
	@mkdir -p services/identity-service/certs
	@if [ ! -f services/identity-service/certs/private.pem ]; then \
		openssl genpkey -algorithm RSA -out services/identity-service/certs/private.pem -pkeyopt rsa_keygen_bits:2048; \
		openssl rsa -pubout -in services/identity-service/certs/private.pem -out services/identity-service/certs/public.pem; \
	fi