#!/bin/bash

REUSE=0
FAIL=0
CMP=0
CHANGED=0

# list of files to check
declare -a files=("noxfile.py" "modules-list.txt" "testing-modules-list.txt")

# compare current and previous file
# if the are different, set REUSE to False
compare_files() {
    cmp --silent $1 $2

    CMP=$?
    if [[ ${REUSE} -eq 0 ]]; then
        REUSE=$?
    fi
}

# set FAIL=1 if any of the config files are missing
for fname in "${files[@]}"; do
    if [[ ! -f ${fname} ]]; then
        echo "file ${fname} is missing." >> runtests.log
        FAIL=1
    fi
done

if [[ ${FAIL} -eq 1 ]]; then
    echo "" >> runtests.log
    echo "**************************************" >> runtests.log
    echo "cannot run tests due to missing files." >> runtests.log
    echo "**************************************" >> runtests.log
    echo "" >> runtests.log
fi

for fname in "${files[@]}"; do
    if [[ ! -f ${fname%.*}.prev ]]; then
        echo "file ${fname%.*}.prev is missing." >>runtests.log
        REUSE=1
        continue
    fi

    compare_files ${fname} ${fname%.*}.prev

    if [[ "${CMP}" -eq 1 ]]; then
        CHANGED=1
        echo "file comparison determined ${fname} has changed" >> runtests.log
    fi
done

if [[ ${REUSE} -eq 1 || ${CHANGED} -eq 1 ]]; then
    echo "" >> runtests.log
    echo "" >> runtests.log
    echo "*********************************************************" >> runtests.log
    echo "cannot reuse environemts due to missing or changed files." >> runtests.log
    echo "*********************************************************" >> runtests.log
    echo "" >> runtests.log
fi

if [[ ${FAIL} -eq 1 ]]; then
    exit 1
fi

conda develop /app

if [[ "${REUSE}" -eq 0 ]]; then
    nox -R -s tests
else
    nox -s tests
fi


# make backup copies of module-list.txt and noxfile.py
mv /app/modules-list.txt /app/modules-list.prev
mv /app/testing-modules-list.txt /app/testing-modules-list.prev
mv /app/noxfile.py /app/noxfile.prev

# remove code directories
rm -rf /app/tests /app/anagram /app/assets

tail -f /dev/null
