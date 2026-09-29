package it.unive.jlisa.witness.validator.parser;

import it.unive.jlisa.witness.validator.ValidationException;
import it.unive.jlisa.witness.validator.model.BenchmarkProperties;
import org.apache.commons.io.FilenameUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.yaml.snakeyaml.LoaderOptions;
import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.constructor.SafeConstructor;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class BenchmarkPropertiesParser {
    private static final Logger LOG = LogManager.getLogger(BenchmarkPropertiesParser.class);

    private BenchmarkPropertiesParser() {
    }

    private static Map<String, Object> loadYaml(File file) {
        Yaml yaml = new Yaml(
                new SafeConstructor(new LoaderOptions())
        );

        try (FileReader reader = new FileReader(file)) {
            Object loaded = yaml.load(reader);

            if (!(loaded instanceof Map<?, ?> map)) {
                throw new RuntimeException("YAML witness root is not a mapping");
            }
            return (Map<String, Object>) map;

        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public static BenchmarkProperties parse(File file) throws FileNotFoundException {
        Map<String, Object> properties = loadYaml(file);
        List<File> inputFiles = new ArrayList<>();
        if (properties.get("input_files") instanceof List){
            inputFiles.addAll(
                    ((List<?>) properties.get("input_files")).stream()
                            .map((f) -> {
                                if (f instanceof String) {
                                    Path path = Paths.get(file.getParent(), (String) f);
                                    return path.toFile();
                                } else {
                                    return null;
                                }
                            }).toList()
            );
        }

        File benchDir = inputFiles.getLast();

        if (!file.getName().contains(benchDir.getName())) {
            throw new FileNotFoundException("Benchmark directory not found, " + file.getName() + " expected");
        }

        return new BenchmarkProperties(inputFiles, benchDir);
    }
}
