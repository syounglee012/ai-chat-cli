.PHONY: test install run

test:
	@source venv/bin/activate && pytest test_agent.py -v

install:
	@python3 -m venv venv
	@source venv/bin/activate && pip install -r requirements.txt

run:
	@./chat.sh
