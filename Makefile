.PHONY: show
show:
	@echo "Showing!"

.PHONY: clean
clean:  
	@find . -name "*.pyc" -delete
