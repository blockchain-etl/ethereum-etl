# Initialise `ENV` variable to `dev` if `ENV` is not a defined environment variable
ENV?=dev
# Extract current repo's URL and remove the `.git` suffix
repo_url:=$(shell git config --get remote.origin.url)
repo_url:=$(repo_url:.git=)
aws_account:=625457032841

# Declare aws region
aws_region:=us-west-2
ecr_main_repository:=im-data-blockchain-ethereum-etl-main-${ENV}
ecr_url:=$(aws_account).dkr.ecr.$(aws_region).amazonaws.com
# Declare default image name to be built
image_name:=im-data-blockchain-ethereum-etl-main
tag_commit:=$(shell git log --format=short --pretty="format:%h" -1)
command=$(cmd)

############################################################################################################################################################
# Make command to build Docker image                                                                                                                  ######
# - `--platform linux/amd64`. ==> for linux/amd65 platform                                                                                            ######
############################################################################################################################################################

docker.build.main:
	docker build --platform linux/amd64 -t $(image_name)-$(ENV):$(tag_commit) -f Dockerfile .

############################################################################################################################################################
# Make command to build docker image and publish image to AWS ECR                                                                                     ######
# - `ecr.push: docker.build`  ==> Invokes `docker.build` before executing steps below                                                                 ######
############################################################################################################################################################

define push_image
	docker tag $1:$(tag_commit) $(ecr_url)/$1:$(tag_commit)
	docker push $(ecr_url)/$1:$(tag_commit)
	docker tag $1:$(tag_commit) $(ecr_url)/$1:latest
	docker push $(ecr_url)/$1:latest
endef

ecr.login:
	aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $(ecr_url)

ecr.push.main: docker.build.main ecr.login
	$(call push_image,${ecr_main_repository})

ecr.push.action: docker.build.main
	$(call push_image,${ecr_main_repository})