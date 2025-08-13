package com.example.devopsmigration.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.example.devopsmigration.model.Pipeline;
import com.example.devopsmigration.model.PipelineSource;
import com.example.devopsmigration.model.PipelineStatus;
import com.example.devopsmigration.repo.PipelineRepository;

@RestController
@RequestMapping("/api/pipelines")
public class PipelineController {
	private final PipelineRepository repository;

	public PipelineController(PipelineRepository repository) {
		this.repository = repository;
	}

	@GetMapping
	public List<Pipeline> list() {
		return repository.findAll();
	}

	@PostMapping
	public Pipeline create(@RequestBody Pipeline pipeline) {
		if (pipeline.getSource() == null) {
			pipeline.setSource(PipelineSource.JENKINS);
		}
		if (pipeline.getStatus() == null) {
			pipeline.setStatus(PipelineStatus.PENDING);
		}
		return repository.save(pipeline);
	}

	@PostMapping("/{id}/migrate")
	public ResponseEntity<Pipeline> migrate(@PathVariable Long id) {
		return repository.findById(id)
			.map(p -> {
				p.setSource(PipelineSource.GITHUB_ACTIONS);
				p.setStatus(PipelineStatus.MIGRATED);
				return ResponseEntity.ok(repository.save(p));
			})
			.orElse(ResponseEntity.notFound().build());
	}
} 