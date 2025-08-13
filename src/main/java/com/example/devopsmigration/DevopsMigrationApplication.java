package com.example.devopsmigration;

import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import com.example.devopsmigration.model.Pipeline;
import com.example.devopsmigration.model.PipelineSource;
import com.example.devopsmigration.model.PipelineStatus;
import com.example.devopsmigration.repo.PipelineRepository;

@SpringBootApplication
public class DevopsMigrationApplication {
	public static void main(String[] args) {
		SpringApplication.run(DevopsMigrationApplication.class, args);
	}

	@Bean
	CommandLineRunner seedData(PipelineRepository repository) {
		return args -> {
			if (repository.count() == 0) {
				repository.save(new Pipeline(null, "Legacy Build", PipelineSource.JENKINS, PipelineStatus.PENDING));
				repository.save(new Pipeline(null, "API Service", PipelineSource.JENKINS, PipelineStatus.PENDING));
				repository.save(new Pipeline(null, "Web Frontend", PipelineSource.GITHUB_ACTIONS, PipelineStatus.MIGRATED));
			}
		};
	}
} 