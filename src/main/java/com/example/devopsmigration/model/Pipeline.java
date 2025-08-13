package com.example.devopsmigration.model;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "pipelines")
public class Pipeline {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	private String name;

	@Enumerated(EnumType.STRING)
	private PipelineSource source;

	@Enumerated(EnumType.STRING)
	private PipelineStatus status;

	public Pipeline() {}

	public Pipeline(Long id, String name, PipelineSource source, PipelineStatus status) {
		this.id = id;
		this.name = name;
		this.source = source;
		this.status = status;
	}

	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public PipelineSource getSource() {
		return source;
	}

	public void setSource(PipelineSource source) {
		this.source = source;
	}

	public PipelineStatus getStatus() {
		return status;
	}

	public void setStatus(PipelineStatus status) {
		this.status = status;
	}
} 