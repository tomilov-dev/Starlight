import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { IMDbMovieExtended } from '../../models/movie.model';
import { DataService } from '../../services/data.service';

@Component({
  selector: 'app-movie',
  templateUrl: './movie.component.html',
  styleUrl: './movie.component.css',
})
export class MovieComponent implements OnInit {
  slug: string = '';
  movie: IMDbMovieExtended | undefined;

  constructor(
    private route: ActivatedRoute,
    private dataService: DataService
  ) {}

  ngOnInit(): void {
    this.slug = this.route.snapshot.params['slug'];
    this.loadMovieData();
  }

  loadMovieData() {
    this.dataService.getMovie(this.slug).subscribe({
      next: (data) => {
        console.log(data);
        this.movie = data;
      },
      error: (error) => {
        console.error("Can't request movie from api!", error);
      },
    });
  }
}
