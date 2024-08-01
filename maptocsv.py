
@RestController
@RequestMapping("/api")
public class FileUploadController {

    @PostMapping("/upload")
    public String handleFileUpload(@RequestParam("file") MultipartFile file) {
        List<ObjectNode> finalDataList = new ArrayList<>();
        ObjectMapper mapper = new ObjectMapper();

        try (InputStream inputStream = file.getInputStream();
             Workbook workbook = new XSSFWorkbook(inputStream)) {

            // Read class data
            Sheet classDataSheet = workbook.getSheetAt(0);
            List<ObjectNode> dataList = new ArrayList<>();
            for (Row row : classDataSheet) {
                if (row.getRowNum() == 0) continue; // Skip header
                String className = row.getCell(0).getStringCellValue();
                String classDesc = row.getCell(1).getStringCellValue();

                ObjectNode jdata = mapper.createObjectNode();
                jdata.put("$id", "data://dac.dmc.178756.pbwm.icg/model/v1/" + className);
                jdata.put("$schema", "data://ilcg.core/model/v1/data-model");
                jdata.put("title", className);
                jdata.put("description", classDesc);

                dataList.add(jdata);
            }

            // Read properties data
            Sheet propertiesDataSheet = workbook.getSheetAt(1);
            for (ObjectNode clsdata : dataList) {
                String className = clsdata.get("title").asText();
                List<String> requiredList = new ArrayList<>();
                List<Map<String, Object>> propertiesList = new ArrayList<>();
                List<String> fieldsList = new ArrayList<>();

                for (Row row : propertiesDataSheet) {
                    if (row.getRowNum() == 0) continue; // Skip header
                    String propertyClassName = row.getCell(0).getStringCellValue();
                    if (propertyClassName.equals(className)) {
                        String propertyName = row.getCell(1).getStringCellValue();
                        String required = row.getCell(2).getStringCellValue();
                        String primaryKey = row.getCell(3).getStringCellValue();
                        String propertyDesc = row.getCell(4).getStringCellValue();
                        String type = row.getCell(5).getStringCellValue();

                        if ("Yes".equals(required)) {
                            requiredList.add(propertyName);
                        }

                        if ("Yes".equals(primaryKey)) {
                            fieldsList.add(propertyName);
                        }

                        Map<String, Object> propertyMap = new HashMap<>();
                        propertyMap.put("description", propertyDesc);
                        propertyMap.put("type", type);

                        propertiesList.add(propertyMap);
                    }
                }

                clsdata.put("required", requiredList);
                ArrayNode propertiesArray = clsdata.putArray("properties");
                for (Map<String, Object> propertyMap : propertiesList) {
                    propertiesArray.addPOJO(propertyMap);
                }
                ArrayNode fieldsArray = clsdata.putArray("fields");
                for (String field : fieldsList) {
                    fieldsArray.add(field);
                }

                finalDataList.add(clsdata);
            }

            // Convert final data list to JSON string
            String jsonResult = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(finalDataList);
            // You can save jsonResult to a file or return it as a response
            // For simplicity, we'll return it as a response here
            return jsonResult;

        } catch (IOException e) {
            e.printStackTrace();
            return "File processing error: " + e.getMessage();
        }
    }
}
