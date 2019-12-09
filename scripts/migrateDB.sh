pip install awscli
export S3_HOST='https://s3.embassy.ebi.ac.uk'
export S3_PATH='s3://rdsds-backups/dsds-migration-files/master/'
aws --endpoint-url ${S3_HOST} s3 cp ${S3_PATH} . --recursive
export DATABASE_NAME=$(echo $DATABASE_URL| grep @ | cut -d@ -f2 | grep : | cut -d: -f1)
export OUTPUT_FILE=output-${DATABASE_NAME}
if [ -f ${OUTPUT_FILE} ]; then
        echo "Migration output file ${OUTPUT_FILE} already there, doing nothing!"
        exit 1
else
        psql $DATABASE_URL -c '\copy objects FROM 'objects.csv' CSV HEADER;' >> ${OUTPUT_FILE}
        psql $DATABASE_URL -c '\copy contents FROM 'contents.csv' CSV HEADER;' >> ${OUTPUT_FILE}
        psql $DATABASE_URL -c '\copy checksums FROM 'checksums.csv' CSV HEADER;' >> ${OUTPUT_FILE}
        psql $DATABASE_URL -c '\copy access_methods FROM 'access_methods.csv' CSV HEADER;' >> ${OUTPUT_FILE}
        aws --endpoint-url ${S3_HOST} s3 cp ${OUTPUT_FILE} ${S3_PATH}
fi