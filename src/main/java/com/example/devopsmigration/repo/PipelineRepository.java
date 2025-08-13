package com.example.devopsmigration.repo;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.devopsmigration.model.Pipeline;

public interface PipelineRepository extends JpaRepository<Pipeline, Long> {
} 