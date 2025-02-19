<!-- # Instructions for candidates

This is the Python version of the Payment Gateway challenge. If you haven't already read the [README.md](https://github.com/cko-recruitment) in the root of this organisation, please do so now.

## Template structure
```
├── .editorconfig - don't change this. It ensures a consistent set of rules for submissions when reformatting code
├── .env.example
├── .python-version - Python version used by Pyenv (https://github.com/pyenv/pyenv).
├── Makefile - Makefile with commands such as install, run and test
├── docker-compose.yml - configures the bank simulator
├── pyproject.toml - project metadata, build system and dependencies
├── poetry.lock - Poetry lock file
├── main.py - app's entrypoint
├── payment_gateway_api/ - skeleton FastAPI API
├── imposters/ - contains the bank simulator configuration. Don't change this
└── tests/ - folder for tests
```

Feel free to change the structure of the solution, use a different test library etc.
 -->

## How to run application

### Docker
```bash
$ docker compose up
```

### Local Environment

- Poetry and Python 3.8 must be installed
- Bank service must be running
```bash
$ docker compose up -d bank_simulator
```

Install Dependencies

```bash
$ make install
```

Run application
```bash
$ make run

INFO:     Will watch for changes in these directories: ['/Users/lazaro/workspace/tests/cko/payment-gateway-challenge-python']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [89899] using statreload
INFO:     Started server process [89905]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Running Tests

### From Docker

```bash
$ docker compose run payment_gateway make test

collected 5 items

tests/test_example.py::test_example <- ../Users/lazaro/workspace/tests/cko/payment-gateway-challenge-python/tests/test_example.py PASSED [ 20%]
tests/test_payment_gateway.py::TestPaymentAPI::test_bank_service_unavailable <- ../Users/lazaro/workspace/tests/cko/payment-gateway-challenge-python/tests/test_payment_gateway.py PASSED [ 40%]
tests/test_payment_gateway.py::TestPaymentAPI::test_get_payment <- ../Users/lazaro/workspace/tests/cko/payment-gateway-challenge-python/tests/test_payment_gateway.py PASSED [ 60%]
tests/test_payment_gateway.py::TestPaymentAPI::test_process_payment_authorized <- ../Users/lazaro/workspace/tests/cko/payment-gateway-challenge-python/tests/test_payment_gateway.py PASSED [ 80%]
tests/test_payment_gateway.py::TestPaymentAPI::test_process_payment_declined <- ../Users/lazaro/workspace/tests/cko/payment-gateway-challenge-python/tests/test_payment_gateway.py PASSED [100%]

=================================== 5 passed in 0.26s ===
```

### From local environment

```bash
$ make test
```

## Design Decisions

### How to store payments

I decided to use a simple hashtable to work as a memory database instead of using a persistent database.

The hashtable key is the processed payment id, the value is the response body, so I can retrive information sent to user.
No sensitive information is stored, just the same information sent to user.

The hashtable allows fast data retrieval, as it's O(1) in time complexity to get identifiable data.

### Processing payments

There is a bank service API, currently hard-coded in the application code.
I'm using httpx to send POST requests to this endpoint with a valid body schema.

I decided for Pydantic library to help me on validating data schema, as it allows me to easily setup validation
conditions based on challenge description. These models are stored on `models/payments.py` for now, so we can add more models if application grows in terms of entities and context.

For a valid payment request I'm generating a GUID, saving it on hashtable and returning it to response, allowing future data retrieval.

### Tests

I'm spliting unit and integration tests into different folders.

Unit tests are now calling API directly, just testing behavior and logic, so I'm mocking some API calls for it.
They run fast and cover all expected and edge cases.

Integration tests calls the bank service directly. The idea is that we should have a way to automate test cases that calls real API endpoints (or a staging environment, prefearably), so we can make sure all things are working as expecting, detecting failure points.

### Improvements

Currently, all logic is implemented inside app.py, there is no controller folder, nor utility methods.
This was intentional for now, as we can discuss changes like that in the pair programming stage.

Possible improvements:
- add a controller folder, where payments can be an individual file
- Move API calls to a service class (BankService) instead of using httpx directly, centralizing future changes in the api calls.
- Create a PaymentService class to handle create and get methods, centralizing it's logic and improving test coverage isolation.
- Optimize Dockerfile for production environment by enforcing just production dependencies
- Linters
