#!/bin/bash
# Common script for the array of scripts used by namcap-reports

url="http://abhidg.mine.nu"
output_dir=
repo_files=
template_dir=/usr/share/namcap-reports/templates

process_config() {
	config=$1
	output_dir=$(fgrep -w output_dir "$config" | awk '{print $2}')
	repo_files=$(fgrep -w repo_files "$config" | awk '{print $2}')
	template_dir=$(fgrep -w template_dir "$config" | awk '{print $2}')
	url=$(fgrep -w url "$config" | awk '{print $2}')

	if [ -z "$template_dir" ]; then
		template_dir=/usr/share/namcap-reports/templates
	fi
}

if [ -f /etc/namcap-reports.conf ]; then
	process_config /etc/namcap-reports.conf
fi

if [ -f "$HOME/namcap-reports.conf" ]; then
	process_config "$HOME/.namcap-reports.conf"
fi
