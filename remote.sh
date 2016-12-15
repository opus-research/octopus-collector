#!/usr/bin/env bash
ssh git@opus.les.inf.puc-rio.br './create.sh results_apache_derby/ufal3_results_repo'

ssh git@opus.les.inf.puc-rio.br './create.sh results_apache_tomcat/dengue_results_repo'
git remote add origin git@opus.les.inf.puc-rio.br:/home/git/repositories/results_apache_derby/ufal3_results_repo

git remote add origin git@localhost:/home/git/repositories/results_apache_tomcat/dengue_results_repo

git push -u origin master


git clone git@opus.les.inf.puc-rio.br:/home/git/repositories/results_apache_tomcat/ufal1_results_repo
ssh git@opus.les.inf.puc-rio.br './create.sh results_apache_tomcat/ufal1_results_repo'
git remote add origin git@opus.les.inf.puc-rio.br:/home/git/repositories/results_apache_tomcat/ufal1_results_repo


git clone git@opus.les.inf.puc-rio.br:/home/git/repositories/results_apache_derby/ufal1_results_repo
ssh git@opus.les.inf.puc-rio.br './create.sh results_apache_derby/ufal1_results_repo'
git remote add origin git@opus.les.inf.puc-rio.br:/home/git/repositories/results_apache_derby/ufal1_results_repo


ssh git@opus.les.inf.puc-rio.br './create.sh results_apache_tomcat/ufal3_results_repo'
git remote add origin git@opus.les.inf.puc-rio.br:/home/git/repositories/results_apache_tomcat/ufal3_results_repo
git push -u origin master


ssh git@opus.les.inf.puc-rio.br './create.sh results_apache_derby/dengue_results_repo'
git remote add origin git@opus.les.inf.puc-rio.br:/home/git/repositories/results_apache_derby/dengue_results_repo
git push -u origin master



ssh git@opus.les.inf.puc-rio.br './create.sh results_apache_derby/ufal2_results_repo'
git remote add origin git@opus.les.inf.puc-rio.br:/home/git/repositories/results_apache_derby/ufal2_results_repo
git push -u origin master