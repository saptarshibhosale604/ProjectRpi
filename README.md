# bash README.md

# SSH
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/GitAuthentication/ProjectRpi_01/id_rsa

git status
git add .
git status

echo commitMessage
read commitMessage

git commit -m "$commitMessage"
git push 

