VERSION:=0.1

build:
	docker build -t enseed/coredns-ctl:${VERSION} .

push:
	docker push enseed/coredns-ctl:${VERSION}
